import logging

import sqlalchemy

from peerscout.utils.collection import groupby_to_dict, applymap_dict

LOGGER = logging.getLogger(__name__)


class StageNames:
    REVIEW_RECEIVED = 'Review Received'


class ManuscriptPersonStageService:
    def __init__(self, db):
        self._db = db

    def get_person_ids_by_version_id_for_stage_names(self, version_ids, stage_names):
        db = self._db
        stage_table = db.manuscript_stage.table
        return applymap_dict(groupby_to_dict(
            db.session.query(
                stage_table.version_id,
                stage_table.person_id
            ).filter(
                sqlalchemy.and_(
                    stage_table.version_id.in_(version_ids),
                    stage_table.stage_name.in_(stage_names)
                )
            ).all(),
            lambda row: row[0],
            lambda row: row[1]
        ), set)
