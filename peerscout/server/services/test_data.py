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
  'first-name': 'Laura',
  'last-name': 'Laudson'
}

PERSON3 = {
  **PERSON1,
  PERSON_ID: PERSON_ID3,
  'first-name': 'Mike',
  'last-name': 'Michelson'
}
