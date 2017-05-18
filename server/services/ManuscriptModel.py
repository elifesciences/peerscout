import logging

import sqlalchemy

NAME = 'ManuscriptModel'

DECISIONS_ACCEPTED = set([
  'Accept Full Submission', 'Auto-Accept'
])

TYPES_ACCEPTED = set([
  'Research Article', 'Short Report', 'Tools and Resources', 'Research Advance'
])

def filter_accepted_manuscript_versions(manuscript_versions):
  return manuscript_versions[
    manuscript_versions['decision'].isin(DECISIONS_ACCEPTED)
  ]

def filter_research_articles(manuscript_versions):
  logging.getLogger(NAME).debug(
    "manuscript types: %s", manuscript_versions['manuscript-type'].unique()
  )
  return manuscript_versions[
    manuscript_versions['manuscript-type'].isin(
      ['Research Article', 'Initial Submission: Research Article'])
  ]

def is_manuscript_accepted(manuscript):
  return manuscript.get('decision', None) in DECISIONS_ACCEPTED

def is_manuscript_type_relevant(manuscript):
  return manuscript.get('manuscript_type') in TYPES_ACCEPTED

def is_manuscript_relevant(manuscript):
  return is_manuscript_accepted(manuscript) and is_manuscript_type_relevant(manuscript)

class ManuscriptModel(object):
  def __init__(self, db):
    manuscript_version_table = db['manuscript_version']

    self.valid_version_ids = set(x[0] for x in db.session.query(
      manuscript_version_table.table.version_id
    ).filter(
      sqlalchemy.and_(
        manuscript_version_table.table.decision.in_(
          DECISIONS_ACCEPTED
        ),
        manuscript_version_table.table.manuscript_type.in_(
          TYPES_ACCEPTED
        )
      )
    ).all())

  def get_valid_manuscript_version_ids(self):
    return self.valid_version_ids
