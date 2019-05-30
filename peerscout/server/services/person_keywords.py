import logging

import sqlalchemy

from ...shared.database_schema import Person

LOGGER = logging.getLogger(__name__)


def get_person_ids_of_person_keywords_scores(person_keyword_scores):
    return person_keyword_scores.keys()


class PersonKeywordService:
    def __init__(self, db):
        self._db = db

    @staticmethod
    def from_database(db):
        return PersonKeywordService(db)

    def _query(self, columns):
        db = self._db
        return db.session.query(*columns).join(
            db.person.table,
            sqlalchemy.and_(
                db.person.table.person_id == db.person_keyword.table.person_id,
                db.person.table.status == Person.Status.ACTIVE
            )
        )

    def get_all_keywords(self):
        return set(
            r[0] for r in
            self._query([self._db.person_keyword.table.keyword]).distinct().all()
        )

    def get_keyword_scores(self, keyword_list):
        if not keyword_list:
            return {}
        num_keywords = len(keyword_list)
        db = self._db
        return dict((keyword, count / num_keywords) for keyword, count in self._query([
            db.person_keyword.table.person_id,
            sqlalchemy.func.count(db.person_keyword.table.person_id)
        ]).filter(
            sqlalchemy.func.lower(db.person_keyword.table.keyword).in_(
                [s.lower() for s in keyword_list]
            )
        ).group_by(db.person_keyword.table.person_id).all())
