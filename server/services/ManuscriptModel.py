import sqlalchemy

NAME = 'ManuscriptModel'

class ManuscriptModel(object):
  def __init__(self, db, valid_decisions=None, valid_manuscript_types=None):
    self.valid_decisions = valid_decisions or []
    self.valid_manuscript_types = valid_manuscript_types or []
    manuscript_version_table = db['manuscript_version']

    conditions = [
      manuscript_version_table.table.decision.in_(
        self.valid_decisions
      ) if self.valid_decisions else None,
      manuscript_version_table.table.manuscript_type.in_(
        self.valid_manuscript_types
      ) if self.valid_manuscript_types else None
    ]
    conditions = [c for c in conditions if c is not None]

    valid_version_ids_query = db.session.query(
      manuscript_version_table.table.version_id
    )
    if len(conditions) > 0:
      valid_version_ids_query = valid_version_ids_query.filter(
        sqlalchemy.and_(*conditions)
      )

    self.valid_version_ids = set(x[0] for x in valid_version_ids_query.all())

  def is_manuscript_relevant(self, manuscript):
    return (
      (
        len(self.valid_decisions) == 0 or
        manuscript.get('decision', None) in self.valid_decisions
      ) and (
        len(self.valid_manuscript_types) == 0 or
        manuscript.get('manuscript_type') in self.valid_manuscript_types
      )
    )

  def get_valid_manuscript_version_ids(self):
    return self.valid_version_ids
