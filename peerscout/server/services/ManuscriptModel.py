from typing import Set

import sqlalchemy

NAME = 'ManuscriptModel'

class ManuscriptModel(object):
  def __init__(
    self, db,
    valid_decisions=None, valid_manuscript_types=None,
    published_decisions=None, published_manuscript_types=None):

    self.db = db
    self.valid_decisions = valid_decisions or []
    self.valid_manuscript_types = valid_manuscript_types or []
    self.published_decisions = published_decisions or []
    self.published_manuscript_types = published_manuscript_types or []

    self.valid_version_ids = self._get_version_ids_by_decisions_and_types(
      self.valid_decisions, self.valid_manuscript_types
    )

  def _get_version_ids_by_decisions_and_types(self, decisions, manuscript_types):
    # pylint: disable=C0121
    manuscript_version_table = self.db['manuscript_version']

    conditions = [
      sqlalchemy.or_(
        manuscript_version_table.table.is_published == True,
        # TODO we shouldn't include blank decisions but as this is currently also used 
        #   when searching by manuscript number, it would have an undesired result
        manuscript_version_table.table.decision == None,
        manuscript_version_table.table.decision.in_(
          decisions
        )
      ) if decisions else None,
      sqlalchemy.or_(
        manuscript_version_table.table.manuscript_type.in_(
          manuscript_types
        )
       ) if manuscript_types else None
    ]
    conditions = [c for c in conditions if c is not None]

    version_ids_query = self.db.session.query(
      manuscript_version_table.table.version_id
    )
    if len(conditions) > 0:
      version_ids_query = version_ids_query.filter(
        sqlalchemy.and_(*conditions)
      )

    return set(x[0] for x in version_ids_query.all())

  def _manuscript_published_or_matches_decisions_and_types(
    self, manuscript: dict, decisions: Set[str], manuscript_types: Set[str]):

    return (
      (
        manuscript.get('is_published') or
        not decisions or
        manuscript.get('decision') in decisions
      ) and (
        not manuscript_types or
        manuscript.get('manuscript_type') in manuscript_types
      )
    )

  def is_manuscript_published(self, manuscript):
    return self._manuscript_published_or_matches_decisions_and_types(
      manuscript, self.published_decisions, self.published_manuscript_types
    )

  def get_valid_manuscript_version_ids(self):
    return self.valid_version_ids
