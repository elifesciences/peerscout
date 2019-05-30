import logging

import sqlalchemy

from ...shared.database_schema import Person

LOGGER = logging.getLogger(__name__)


class PersonRoleService:
    def __init__(self, db):
        self._db = db

    @staticmethod
    def from_database(db):
        return PersonRoleService(db)

    def filter_person_ids_by_role(self, person_ids, role):
        if not role:
            return person_ids
        db = self._db
        raw_result = db.session.query(
            db.person_role.table.person_id
        ).join(
            db.person.table,
            sqlalchemy.and_(
                db.person.table.person_id == db.person_role.table.person_id,
                db.person.table.status == Person.Status.ACTIVE
            )
        ).filter(
            sqlalchemy.and_(
                db.person_role.table.person_id.in_(person_ids),
                db.person_role.table.role == role
            )
        ).all()
        result = set(r[0] for r in raw_result)
        LOGGER.debug('filtered person ids by role: %d -> %d (role=%s)',
                     len(person_ids), len(result), role)
        return result

    def user_has_role_by_email(self, email, role):
        if not role:
            return False
        db = self._db
        result = db.session.query(
            sqlalchemy.func.count(db.person.table.person_id)
        ).filter(
            sqlalchemy.and_(
                db.person.table.person_id == db.person_role.table.person_id,
                db.person.table.status == Person.Status.ACTIVE,
                db.person.table.email == email
            )
        ).join(
            db.person_role.table,
            sqlalchemy.and_(
                db.person_role.table.person_id == db.person.table.person_id,
                db.person_role.table.role == role,
            )
        ).scalar() > 0
        LOGGER.debug('user_has_role_by_email: email=%s, role=%s -> %s', email, role, result)
        return result

    def get_user_roles_by_email(self, email):
        db = self._db
        roles = set(x[0] for x in db.session.query(
            db.person_role.table.role
        ).select_from(db.person.table).filter(
            sqlalchemy.and_(
                db.person.table.person_id == db.person_role.table.person_id,
                db.person.table.status == Person.Status.ACTIVE,
                db.person.table.email == email
            )
        ).join(
            db.person_role.table,
            db.person_role.table.person_id == db.person.table.person_id
        ).all())
        LOGGER.debug('get_user_roles_by_email: email=%s, roles=%s', email, roles)
        return roles
