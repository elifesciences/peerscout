import logging
from collections import Counter

import sqlalchemy

from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict
)

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
    LOGGER.debug('filtered person ids by role: %d -> %d (role=%s)', len(person_ids), len(result), role)
    return result
