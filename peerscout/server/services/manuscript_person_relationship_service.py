import logging

import sqlalchemy

from peerscout.utils.collection import groupby_to_dict, applymap_dict

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

  def get_person_ids_by_version_id_for_relationship_types(self, version_ids, relationship_types):
    if not relationship_types or not version_ids:
      return {}
    db = self._db
    relationship_tables = [
      _get_relationship_table(db, relationship_type)
      for relationship_type in relationship_types
    ]
    queries = [
      db.session.query(
        relationship_table.version_id,
        relationship_table.person_id
      ).filter(
        relationship_table.version_id.in_(version_ids)
      )
      for relationship_table in relationship_tables
    ]
    q = queries[0] if len(queries) == 1 else db.session.query(sqlalchemy.union(*queries))
    return applymap_dict(groupby_to_dict(
      q.all(),
      lambda row: row[0],
      lambda row: row[1]
    ), set)
