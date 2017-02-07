from .RecommendReviewers import RecommendReviewers


# import pandas as pd

# def read_csv(*args, **kwargs):
#   df_headers = pd.read_csv(*args, **kwargs, nrows=1, encoding='utf-8')
#   parse_dates = []
#   for column in df_headers.columns:
#     if column.endswith('-date'):
#       parse_dates.append(column)
#   return pd.read_csv(*args, **kwargs, encoding='utf-8', parse_dates=parse_dates)

# def column_astype(df, col_name, col_type):
#   df = df.copy()
#   df[col_name] = df[col_name].astype(col_type)
#   return df

# def applymap_dict_list(dict_list, f):
#   return [dict((k, f(v)) for k, v in row.items()) for row in dict_list]

# def nat_to_none(x):
#   return None if type(x) == type(pd.NaT) else x

# def clean_result(result):
#   return applymap_dict_list(result, nat_to_none)

# # def clean_df(df):
# #   # TODO fix replace NaT
# #   #return df.where((pd.notnull(df)), None)
# #   return df.applymap(lambda x: None if type(x) == type(pd.NaT) else x)

# class RecommendReviewers(object):
#   def __init__(self, config):
#     csv_path = '../' + config['csv']['path']
#     self.config = config
#     def get_csv(filename, *args, **kwargs):
#       df = read_csv(csv_path + "/" + filename, *args, **kwargs)
#       print("df {} shape {}".format(filename, df.shape))
#       return df
#     self.manuscripts_df = get_csv("manuscripts.csv")
#     self.manuscript_keywords_df = get_csv("manuscript-keywords.csv")
#     self.authors_df = get_csv("authors.csv")
#     self.persons_df = get_csv("persons-current.csv", low_memory=False, index_col='person-id')
#     # persons_df.shape
#     # self.authors_df.shape
#     # print(self.manuscript_keywords_df.shape)
#     # print(self.manuscripts_df.shape)

#   def find_manuscripts_by_keywords(self, keywords, version_key=None):
#     other_manuscripts = self.manuscript_keywords_df.\
#       drop('sequence', axis=1).\
#       set_index('word').\
#       ix[keywords].\
#       reset_index()
#     other_manuscripts = other_manuscripts[other_manuscripts['version-key'] != version_key].\
#     groupby(['base-manuscript-number', 'manuscript-number', 'version-key']).agg({
#       'word': {
#         'keywords': lambda x: tuple(x),
#         'count': pd.np.size
#       }
#     })['word']
#     return other_manuscripts

#   def find_authors_by_manuscripts(self, manuscripts):
#     print("manuscripts columns:", manuscripts.columns)
#     other_authors = self.authors_df[self.authors_df['base-manuscript-number'].isin(
#       manuscripts.index.get_level_values('base-manuscript-number'))]
#     other_authors = other_authors[['base-manuscript-number', 'author-person-id']].\
#       drop_duplicates()
#     return other_authors

#   def find_manuscripts_by_key(self, version_key):
#     return self.manuscript_keywords_df[
#       self.manuscript_keywords_df['version-key'] == version_key
#     ]
#     # if (version_key is None) or (version_key not in ix):
#     #   return pd.DataFrame([], columns=self.manuscript_keywords_df.columns)
#     # return ix[version_key]

#   def add_author_person_info(self, authors):
#     return authors.merge(
#         right=self.persons_df.reset_index(),
#         how='left',
#         left_on='author-person-id',
#         right_on='person-id')

#   def parse_keywords(self, keywords):
#     if keywords.strip() == '':
#       return []
#     return [keyword.strip() for keyword in keywords.split(',')]

#   def recommend(self, keywords, version_key):
#     keyword_list = self.parse_keywords(keywords)
#     # matching_manuscripts = pd.DataFrame([])
#     if version_key is not None and version_key != '':
#       matching_manuscripts = self.find_manuscripts_by_key(version_key)
#       manuscript_keywords = matching_manuscripts['word']
#       keyword_list += list(manuscript_keywords.values)
#     else:
#       matching_manuscripts = self.find_manuscripts_by_key('')
#     print("keyword_list:", keyword_list)
#     other_manuscripts = self.find_manuscripts_by_keywords(
#       keyword_list
#     )
#     other_authors = self.add_author_person_info(
#       self.find_authors_by_manuscripts(other_manuscripts)).reset_index()
#     print("columns:", other_authors.columns)
#     return {
#       'potential-authors': clean_result(
#         other_authors\
#         .reset_index()\
#         [['author-person-id', 'base-manuscript-number',
#           'title', 'first-name', 'middle-name', 'last-name']]\
#         .to_dict(orient='records')),
#       'matching-matching_manuscripts': clean_result(
#         matching_manuscripts\
#         .reset_index()\
#         [['base-manuscript-number', 'manuscript-number', 'version-key']]\
#         .drop_duplicates()
#         .to_dict(orient='records')
#       )
#     }
