from ...shared.database_schema import Person

PERSON_ID = 'person_id'

PERSON_ID1 = 'person1'
PERSON_ID2 = 'person2'
PERSON_ID3 = 'person3'

PERSON1 = {
  PERSON_ID: PERSON_ID1,
  'first_name': 'John',
  'last_name': 'Smith',
  'status': Person.Status.ACTIVE,
  'is_early_career_researcher': False
}

PERSON2 = {
  **PERSON1,
  PERSON_ID: PERSON_ID2,
  'first_name': 'Laura',
  'last_name': 'Laudson'
}

PERSON3 = {
  **PERSON1,
  PERSON_ID: PERSON_ID3,
  'first_name': 'Mike',
  'last_name': 'Michelson'
}

MANUSCRIPT_ID = 'manuscript_id'
VERSION_ID = 'version_id'

def version_id(manuscript_no, version_no):
  return '{}-{}'.format(manuscript_no, version_no)

MANUSCRIPT_ID1 = '12345'
MANUSCRIPT_VERSION_ID1 = version_id(MANUSCRIPT_ID1, 1)
MANUSCRIPT_TITLE1 = 'Manuscript Title1'
MANUSCRIPT_ABSTRACT1 = 'Manuscript Abstract 1'

MANUSCRIPT_ID2 = '22222'
MANUSCRIPT_VERSION_ID2 = version_id(MANUSCRIPT_ID2, 2)
MANUSCRIPT_TITLE2 = 'Manuscript Title2'

MANUSCRIPT_ID3 = '33333'
MANUSCRIPT_VERSION_ID3 = version_id(MANUSCRIPT_ID3, 3)
MANUSCRIPT_TITLE3 = 'Manuscript Title3'

MANUSCRIPT_ID_FIELDS1 = {
  MANUSCRIPT_ID: MANUSCRIPT_ID1,
  VERSION_ID: MANUSCRIPT_VERSION_ID1
}

MANUSCRIPT_ID_FIELDS2 = {
  MANUSCRIPT_ID: MANUSCRIPT_ID2,
  VERSION_ID: MANUSCRIPT_VERSION_ID2
}

MANUSCRIPT_ID_FIELDS3 = {
  MANUSCRIPT_ID: MANUSCRIPT_ID3,
  VERSION_ID: MANUSCRIPT_VERSION_ID3
}

create_manuscript_id_fields = lambda i: ({
  MANUSCRIPT_ID: str(i),
  VERSION_ID: version_id(str(i), 1)
})

MANUSCRIPT_ID_FIELDS4 = create_manuscript_id_fields(4)
MANUSCRIPT_ID_FIELDS5 = create_manuscript_id_fields(5)

DECISSION_ACCEPTED = 'Accept Full Submission'
DECISSION_REJECTED = 'Reject Full Submission'

TYPE_RESEARCH_ARTICLE = 'Research Article'

PUBLISHED_DECISIONS = {DECISSION_ACCEPTED}
PUBLISHED_MANUSCRIPT_TYPES = {TYPE_RESEARCH_ARTICLE}

VALID_DECISIONS = PUBLISHED_DECISIONS | {DECISSION_REJECTED}
VALID_MANUSCRIPT_TYPES = PUBLISHED_MANUSCRIPT_TYPES

MANUSCRIPT_VERSION1 = {
  **MANUSCRIPT_ID_FIELDS1,
  MANUSCRIPT_ID: MANUSCRIPT_ID1,
  'doi': None,
  'title': MANUSCRIPT_TITLE1,
  'decision': DECISSION_ACCEPTED,
  'manuscript_type': TYPE_RESEARCH_ARTICLE,
  'is_published': True
}

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'

MANUSCRIPT_KEYWORD1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'keyword': KEYWORD1
}
