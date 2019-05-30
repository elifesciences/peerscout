import logging
from typing import Dict, List, Set, Tuple

import sqlalchemy

from peerscout.utils.collection import groupby_to_dict, applymap_dict, filter_none
from peerscout.shared.database import Database
from peerscout.shared.database_types import PersonId, VersionId

LOGGER = logging.getLogger(__name__)


class RelationshipTypes:
    AUTHOR = 'author'
    CORRESPONDING_AUTHOR = 'corresponding_author'
    EDITOR = 'editor'
    SENIOR_EDITOR = 'senior_editor'
    REVIEWER = 'reviewer'
    POTENTIAL_EDITOR = 'potential_editor'
    POTENTIAL_REVIEWER = 'potential_reviewer'


RelationshipType = str

TABLE_NAME_BY_RELATIONSHIP_TYPE = {
    RelationshipTypes.AUTHOR: 'manuscript_author',
    RelationshipTypes.CORRESPONDING_AUTHOR: 'manuscript_author',
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


def _get_relationship_tables(db, relationship_types):
    return [
        _get_relationship_table(db, relationship_type)
        for relationship_type in relationship_types
    ]


def _union(db, queries):
    return db.session.query(sqlalchemy.union_all(*queries).alias())


def _get_person_id_version_id_relationship_type_query(
        db: Database, relationship_type: RelationshipType,
        person_ids: List[PersonId] = None, version_ids: List[VersionId] = None
    ) -> List[Tuple[PersonId, VersionId, RelationshipType]]:

    relationship_table = _get_relationship_table(db, relationship_type)
    query = db.session.query(
        relationship_table.person_id,
        relationship_table.version_id,
        sqlalchemy.sql.expression.literal(relationship_type)
    ).filter(
        sqlalchemy.and_(*filter_none([
            relationship_table.person_id.in_(person_ids) if person_ids else None,
            relationship_table.version_id.in_(version_ids) if version_ids else None
        ]))
    )
    if relationship_type == RelationshipTypes.CORRESPONDING_AUTHOR:
        query = query.filter(
            db.manuscript_author.table.is_corresponding_author == True
        )
    return query


def _get_person_id_version_id_relationship_type_tuples(
        db: Database, relationship_types: List[RelationshipType],
        person_ids: List[PersonId] = None, version_ids: List[VersionId] = None
    ) -> List[Tuple[PersonId, VersionId, RelationshipType]]:

    if not relationship_types or (not person_ids and not version_ids):
        return []

    return _union(db, [
        _get_person_id_version_id_relationship_type_query(
            db, relationship_type=relationship_type,
            person_ids=person_ids, version_ids=version_ids
        )
        for relationship_type, relationship_table in zip(
            relationship_types,
            _get_relationship_tables(db, relationship_types)
        )
    ])


def _group_person_ids_by_version_id(
        person_id_version_id_relationship_type_tuples: List[
            Tuple[PersonId, VersionId, RelationshipType]
        ]
    ) -> Dict[VersionId, Set[PersonId]]:

    return applymap_dict(groupby_to_dict(
        person_id_version_id_relationship_type_tuples,
        lambda x: x[1],
        lambda x: x[0]
    ), set)


def _group_version_id_relationship_types_by_relationship_type(
        version_id_relationship_type_tuples: List[Tuple[VersionId, RelationshipType]]
    ) -> Dict[RelationshipType, Set[VersionId]]:

    return applymap_dict(groupby_to_dict(
        version_id_relationship_type_tuples,
        lambda x: x[1],
        lambda x: x[0]
    ), set)


def _group_by_person_id_then_relationship_type(
        person_id_version_id_relationship_type_tuples: List[
            Tuple[PersonId, VersionId, RelationshipType]
        ]
    ) -> Dict[PersonId, Dict[RelationshipType, Set[VersionId]]]:

    return applymap_dict(groupby_to_dict(
        person_id_version_id_relationship_type_tuples,
        lambda x: x[0],
        lambda x: x[1:]
    ), _group_version_id_relationship_types_by_relationship_type)


class ManuscriptPersonRelationshipService:
    def __init__(self, db: Database):
        self._db = db

    def get_person_ids_by_version_id_for_relationship_types(
            self, version_ids: List[VersionId], relationship_types: List[RelationshipType]
        ) -> Dict[VersionId, Set[PersonId]]:

        return _group_person_ids_by_version_id(
            _get_person_id_version_id_relationship_type_tuples(
                self._db, version_ids=version_ids, relationship_types=relationship_types
            )
        )

    def get_version_ids_by_person_id_and_relationship_type(
            self,
            person_ids: List[PersonId],
            relationship_types: List[RelationshipType]
        ) -> Dict[PersonId, Dict[RelationshipType, Set[VersionId]]]:

        return _group_by_person_id_then_relationship_type(
            _get_person_id_version_id_relationship_type_tuples(
                self._db, person_ids=person_ids, relationship_types=relationship_types
            )
        )
