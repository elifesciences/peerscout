from os import makedirs
import os
from os.path import isfile

import numpy as np
import pandas as pd
import pyLDAvis
import pyLDAvis.sklearn
from sklearn.decomposition import TruncatedSVD
import bokeh.io as bokeh_io
from bokeh.io import show, output_file as bokeh_output_file
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool
import matplotlib.cm as cmx
import matplotlib.colors as matplotlib_colors
from bhtsne import tsne
import gensim

from lda_utils import train_lda
from convertUtils import flatten, unescape_and_strip_tags_if_not_none

def get_cmap(N):
  '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct
  RGB color.'''
  color_norm  = matplotlib_colors.Normalize(vmin=0, vmax=N-1)
  scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')
  def map_index_to_rgb_color(index):
      return scalar_map.to_rgba(index)
  return map_index_to_rgb_color

def sets_to_colors(sets, include=None):
  if include is None:
    include = sorted(list(set(flatten(sets))))
  cmap = get_cmap(len(include))
  item_color_map = dict((k, cmap(i)) for i, k in enumerate(include))
  filtered_sets = [
    [k for k in k_list if k in item_color_map]
    for k_list in sets
  ]
  return [
    np.mean([
      item_color_map[s]
      for s in s_list
    ], axis=0)
    if len(s_list) > 0
    else None
    for s_list in filtered_sets
  ]

def propbabilities_to_colors(probabilities):
  probabilities = np.array(probabilities)
  column_count = len(probabilities[0])
  print("column count:", column_count)
  cmap = get_cmap(column_count)
  column_colors = [np.array(cmap(i)) for i in range(column_count)]
  color_depth = len(column_colors[0])
  print("color depth:", color_depth)
  result = np.zeros((len(probabilities), column_count, color_depth))
  # for each color, multiply the color component
  for ci in range(column_count):
    for cc in range(color_depth):
      result[:, ci, cc] = np.multiply(probabilities[:, ci], column_colors[ci][cc])
  # then use the sum of the individual colors per row (probabilities should add up to one)
  result = np.sum(result, axis=1)
  return result

def to_bokeh_colors(colors):
  return [
    "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
    for r, g, b, a in colors
  ]

def bokeh_hover_tool(template):
  if isinstance(template, list):
    template = '\n'.join(["<div>{}</div>".format(s) for s in template])
  return HoverTool(
    tooltips='\n'.join([
      '<div style="display: block; max-width: 300px; max-height: 150px; overflow: hidden;">',
      template,
      '</div>'
    ])
  )

def bokeh_show_scatter(data=None, source=None, tools=None, fill_alpha=0.2, filename=None):
  if source is None:
    source = ColumnDataSource(data=data)

  DEFAULT_TOOLS=(
    "resize,crosshair,pan,wheel_zoom,box_zoom,zoom_in,zoom_out,reset,box_select,lasso_select"
  )

  figure_tools = DEFAULT_TOOLS.split(',')
  if tools is not None:
    figure_tools = tools + figure_tools

  p = figure(tools=figure_tools)
  p.circle(
    'x', 'y', radius='radius', fill_color='colors',
    fill_alpha=fill_alpha, line_color=None, source=source)

  if filename is not None:
    bokeh_output_file(filename)
    bokeh_io.save(p, filename=filename)
  else:
    show(p)

def generate_lda_charts(data, charts_path):
  makedirs(charts_path, exist_ok=True)
  abstracts = data['abstracts']
  texts = data['texts']
  subject_areas = data['subject_areas']
  ids = data['ids']
  # max_items = 1000
  # abstracts = abstracts[:max_items]
  # texts = texts[:max_items]
  # subject_areas = subject_areas[:max_items]
  # ids = ids[:max_items]

  topics = [10, 15, 20, 30, 40, 50]
  print("topics:", list(topics))

  vectorizer = None
  vectorized = None

  subject_area_colors = sets_to_colors(subject_areas)

  for n_topics in topics:
    lda_ldavis_output_filename = os.path.join(
      charts_path,
      'lda-sense2vec-topics{}-samples{}-ldavis.html'.format(n_topics, len(texts))
    )
    lda_scatter_output_filename = os.path.join(
      charts_path,
      'lda-sense2vec-topics{}-samples{}-scatter.html'.format(n_topics, len(texts))
    )
    lda_scatter_lda_colors_output_filename = os.path.join(
      charts_path,
      'lda-sense2vec-topics{}-samples{}-scatter-lda-colors.html'.format(n_topics, len(texts))
    )
    if (
      isfile(lda_ldavis_output_filename) and
      isfile(lda_scatter_output_filename) and
      isfile(lda_scatter_lda_colors_output_filename)
    ):
      continue
    print("creating LDA for {} topics".format(n_topics))
    lda_result = train_lda(texts, n_topics=n_topics, vectorizer=vectorizer, vectorized=vectorized)
    lda_prepared = pyLDAvis.sklearn.prepare(
      lda_result.lda,
      lda_result.vectorized,
      lda_result.vectorizer
    )
    vectorizer = lda_result.vectorizer
    vectorized = lda_result.vectorized
    html = pyLDAvis.prepared_data_to_html(lda_prepared)
    with open(lda_ldavis_output_filename, 'w') as f:
      f.write(html)

    tsne_result = tsne(np.array(lda_result.docvecs, dtype='float64'))

    lda_bokeh_data = dict(
      id=ids,
      x=tsne_result[:, 0],
      y=tsne_result[:, 1],
      colors=to_bokeh_colors(subject_area_colors),
      radius=[0.2] * len(texts),
      subject_areas=[", ".join(a) for a in subject_areas],
      abstract=abstracts
    )
    bokeh_show_scatter(
      data=lda_bokeh_data,
      tools=[bokeh_hover_tool([
        '@id: <b>@subject_areas</b>',
        '@abstract</div>'
      ])],
      filename=lda_scatter_output_filename
    )

    bokeh_show_scatter(
      data={
        **lda_bokeh_data,
        'colors': to_bokeh_colors(propbabilities_to_colors(lda_result.docvecs))
      },
      tools=[bokeh_hover_tool([
        '@id: <b>@subject_areas</b>',
        '@abstract</div>'
      ])],
      filename=lda_scatter_lda_colors_output_filename
    )

def generate_doc2vec_charts(data, charts_path):
  makedirs(charts_path, exist_ok=True)
  abstracts = data['abstracts']
  texts = data['texts']
  subject_areas = data['subject_areas']
  ids = data['ids']
  # max_items = 1000
  # abstracts = abstracts[:max_items]
  # texts = texts[:max_items]
  # subject_areas = subject_areas[:max_items]
  # ids = ids[:max_items]

  vec_sizes = [50, 100, 300]
  print("vec_sizes:", list(vec_sizes))

  words_by_sentence = [
    s.split(' ')
    for s in texts
  ]

  sentences = [
    gensim.models.doc2vec.TaggedDocument(words=words, tags=[i])
    for i, words in enumerate(words_by_sentence)
  ]

  subject_area_colors = sets_to_colors(subject_areas)

  for vec_size in vec_sizes:
    doc2vec_scatter_output_filename = os.path.join(
      charts_path,
      'doc2vec-sense2vec-size{}-samples{}-scatter.html'.format(vec_size, len(texts))
    )
    if isfile(doc2vec_scatter_output_filename):
      continue
    print("creating doc2vec for {} vector size".format(vec_size))
    model = gensim.models.Doc2Vec(
      size=vec_size, window=10, min_count=5, workers=2, alpha=0.025, min_alpha=0.025
    )
    model.build_vocab(sentences)
    current_epoch = 0

    for _ in range(20):
      print("epoch", current_epoch, ", alpha:", model.alpha)
      model.train(sentences)
      model.alpha = model.alpha * 0.95 # decrease the learning rate
      model.min_alpha = model.alpha # fix the learning rate, no deca
      current_epoch += 1

    if vec_size <= 50:
      tsne_docvecs = np.array(model.docvecs, dtype='float64')
    else:
      tsne_docvecs = TruncatedSVD(n_components=50).fit_transform(model.docvecs)

    tsne_result = tsne(tsne_docvecs)

    radius = (np.max(tsne_result[:, 0]) - np.min(tsne_result[:, 0])) * 0.007

    bokeh_show_scatter(
      data=dict(
        id=ids,
        x=tsne_result[:, 0],
        y=tsne_result[:, 1],
        colors=to_bokeh_colors(subject_area_colors),
        radius=[radius] * len(texts),
        subject_areas=[", ".join(a) for a in subject_areas],
        abstract=abstracts
      ),
      tools=[bokeh_hover_tool([
        '@id: <b>@subject_areas</b>',
        '@abstract</div>'
      ])],
      filename=doc2vec_scatter_output_filename
    )

def process_article_abstracts(csv_path, charts_path):
  suffix = '-sense2vec'
  text_column = 'abstract' + suffix

  manuscript_versions_all_df = pd.read_csv(csv_path + "/manuscript-versions.csv", low_memory=False)
  manuscript_versions_all_df = manuscript_versions_all_df[
    pd.notnull(manuscript_versions_all_df['abstract'])
  ]
  manuscript_versions_df = (
    manuscript_versions_all_df
    .sort_values(['manuscript-no', 'version-no'])
    .groupby(['manuscript-no'], as_index=False)
    .last()
  )
  manuscript_versions_df['abstract'] = (
    manuscript_versions_df['abstract'].apply(unescape_and_strip_tags_if_not_none)
  )

  manuscript_themes_df = pd.read_csv(csv_path + "/manuscript-themes.csv", low_memory=False)
  subject_areas_df = (
    manuscript_themes_df[['manuscript-no', 'theme']].drop_duplicates()
    .groupby('manuscript-no').agg(lambda x: set(x))['theme']
    .to_frame('subject-areas')
    .reset_index()
  )
  df = pd.read_csv(
    os.path.join(csv_path, 'manuscript-abstracts{}.csv'.format(suffix)),
    low_memory=False
  )
  df = df[
    pd.notnull(df[text_column])
  ][['manuscript-no', text_column]]
  df = (
    df.merge(subject_areas_df, on='manuscript-no')
    .merge(manuscript_versions_df, on='manuscript-no')
  )

  data = {
    'ids': df['manuscript-no'].values,
    'abstracts': df['abstract'].values,
    'texts': df[text_column].values,
    'subject_areas': df['subject-areas'].values
  }
  generate_lda_charts(data, charts_path)
  generate_doc2vec_charts(data, charts_path)

def main():
  csv_path = "../csv"
  charts_path = "../charts"

  process_article_abstracts(csv_path, charts_path)

if __name__ == "__main__":
  main()
