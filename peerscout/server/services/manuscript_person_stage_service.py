import logging

import sqlalchemy

LOGGER = logging.getLogger(__name__)

class StageNames:
  REVIEW_RECEIVED = 'Review Received'

class ManuscriptPersonStageService:
  def __init__(self, db):
    self._db = db

  def get_person_ids_for_version_ids_and_stage_name(self, version_ids, stage_name):
    return self.get_person_ids_for_version_ids_and_stage_names(
      version_ids, [stage_name]
    )

  def get_person_ids_for_version_ids_and_stage_names(self, version_ids, stage_names):
    db = self._db
    stage_table = db.manuscript_stage.table
    return set(
      r[0] for r in
      db.session.query(
        stage_table.person_id
      ).filter(
        sqlalchemy.and_(
          stage_table.version_id.in_(version_ids),
          stage_table.stage_name.in_(stage_names)
        )
      ).all()
    )
