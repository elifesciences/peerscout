import logging

from peerscout.utils.collection import (
  iter_flatten
)

LOGGER = logging.getLogger(__name__)

class RelationshipTypes:
  AUTHOR = 'author'
  EDITOR = 'editor'
  SENIOR_EDITOR = 'senior_editor'
  REVIEWER = 'reviewer'
  POTENTIAL_EDITOR = 'potential_editor'
  POTENTIAL_REVIEWER = 'potential_reviewer'

TABLE_NAME_BY_RELATIONSHIP_TYPE = {
  RelationshipTypes.AUTHOR: 'manuscript_author',
  RelationshipTypes.EDITOR: 'manuscript_editor',
  RelationshipTypes.SENIOR_EDITOR: 'manuscript_senior_editor',
  RelationshipTypes.REVIEWER: 'manuscript_reviewer',
  RelationshipTypes.POTENTIAL_EDITOR: 'manuscript_potential_editor',
  RelationshipTypes.POTENTIAL_REVIEWER: 'manuscript_potential_reviewer'
}

def get_person_ids_of_person_keywords_scores(person_keyword_scores):
  return person_keyword_scores.keys()

def _get_relationship_entity(db, relationship_type):
  return db[TABLE_NAME_BY_RELATIONSHIP_TYPE[relationship_type]]

def _get_relationship_table(db, relationship_type):
  return _get_relationship_entity(db, relationship_type).table

class ManuscriptPersonRelationshipService:
  def __init__(self, db):
    self._db = db

  def get_person_ids_for_version_ids_and_relationship_type(self, version_ids, relationship_type):
    db = self._db
    relationship_table = _get_relationship_table(db, relationship_type)
    return set(
      r[0] for r in
      db.session.query(
        relationship_table.person_id
      ).filter(
        relationship_table.version_id.in_(version_ids)
      ).all()
    )

  def get_person_ids_for_version_ids_and_relationship_types(self, version_ids, relationship_types):
    return set(iter_flatten(
      self.get_person_ids_for_version_ids_and_relationship_type(
        version_ids, relationship_type
      )
      for relationship_type in relationship_types
    ))
