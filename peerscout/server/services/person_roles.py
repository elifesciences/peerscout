import logging
from collections import Counter

from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict
)

from ...shared.database_schema import Person

LOGGER = logging.getLogger(__name__)

class PersonRoleService:
  def __init__(self, role_by_person_id_map):
    self._role_by_person_id_map = role_by_person_id_map

  @staticmethod
  def from_database(db):
    return PersonRoleService.from_person_id_keyword_tuples(
      db.session.query(
        db.person_role.table.person_id,
        db.person_role.table.role
      ).join(
        db.person.table,
        db.person.table.status == Person.Status.ACTIVE
      ).all(),
    )

  @staticmethod
  def from_person_id_keyword_tuples(person_id_role_tuples):
    return PersonRoleService(
      role_by_person_id_map=groupby_to_dict(
        person_id_role_tuples,
        lambda x: x[0],
        lambda x: x[1]
      )
    )

  def filter_person_ids_by_role(self, person_ids, role):
    result = {
      person_id for person_id in person_ids
      if role in self._role_by_person_id_map.get(person_id, [])
    } if role else person_ids
    LOGGER.debug('filtered person ids by role: %d -> %d (role=%s)', len(person_ids), len(result), role)
    return result
