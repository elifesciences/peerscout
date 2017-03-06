
MANUSCRIPT_NO = 'manuscript-no'
VERSION_NO = 'version-no'
# internal composite id
MANUSCRIPT_VERSION_ID = 'manuscript-version-id'

DECISIONS_ACCEPTED = set(['Accept Full Submission', 'Auto-Accept'])
TYPES_ACCEPTED = set([
  'Research Article', 'Short Report', 'Tools and Resources', 'Research Advance'
])

def add_manuscript_version_id(df):
  df[MANUSCRIPT_VERSION_ID] = df[MANUSCRIPT_NO].str.cat(
    df[VERSION_NO].map(str), sep='-')
  return df

def filter_accepted_manuscript_versions(manuscript_versions):
  return manuscript_versions[
    manuscript_versions['decision'].isin(DECISIONS_ACCEPTED)
  ]

def filter_research_articles(manuscript_versions):
  print("manuscript types:", manuscript_versions['manuscript-type'].unique())
  return manuscript_versions[
    manuscript_versions['manuscript-type'].isin(
      ['Research Article', 'Initial Submission: Research Article'])
  ]

def is_manuscript_accepted(manuscript):
  return manuscript.get('decision', None) in DECISIONS_ACCEPTED

def is_manuscript_type_relevant(manuscript):
  return manuscript.get('manuscript-type') in TYPES_ACCEPTED

def is_manuscript_relevant(manuscript):
  return is_manuscript_accepted(manuscript) and is_manuscript_type_relevant(manuscript)

class ManuscriptModel(object):
  def __init__(self, datasets):
    self.manuscript_versions_all_df = add_manuscript_version_id(
      datasets['manuscript-versions'].copy())
    self.manuscript_versions_df = filter_research_articles(filter_accepted_manuscript_versions(
      self.manuscript_versions_all_df
    ))
    self.manuscript_last_versions_df = self.manuscript_versions_df\
      .sort_values(VERSION_NO)\
      .groupby([MANUSCRIPT_NO], as_index=False)\
      .last()
    self.valid_version_ids = (
      self.manuscript_last_versions_df[MANUSCRIPT_VERSION_ID]
    )

  def get_valid_manuscript_version_ids(self):
    return self.valid_version_ids

  def add_manuscript_version_id(self, df):
    return add_manuscript_version_id(df)
