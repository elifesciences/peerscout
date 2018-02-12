from sqlalchemy import (
  Column,
  Boolean,
  DateTime,
  Float,
  Integer,
  LargeBinary,
  PickleType,
  String,
  ForeignKey,
  TIMESTAMP
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql

Base = declarative_base()

SCHEMA_VERSION = 10

class SchemaVersion(Base):
  __tablename__ = "schema_version"

  schema_version_id = Column(String, primary_key=True)
  version = Column(Integer)

class ImportProcessed(Base):
  __tablename__ = "import_processed"

  import_processed_id = Column(String, primary_key=True)
  version = Column(Integer)
  when = Column(TIMESTAMP)

class Person(Base):
  __tablename__ = "person"

  person_id = Column(String, primary_key=True)
  title = Column(String)
  first_name = Column(String)
  middle_name = Column(String)
  last_name = Column(String)
  status = Column(String)
  email = Column(String)
  institution = Column(String)
  is_early_career_researcher = Column(Boolean, nullable=False, default=False)

def create_person_id_fk(**kwargs):
  return Column(
    String,
    ForeignKey('person.person_id', onupdate="CASCADE", ondelete="CASCADE"),
    **kwargs
  )

class PersonDatesNotAvailable(Base):
  __tablename__ = "person_dates_not_available"

  person_id = create_person_id_fk(primary_key=True)
  start_date = Column(DateTime, primary_key=True)
  end_date = Column(DateTime, primary_key=True)

class PersonMembership(Base):
  __tablename__ = "person_membership"

  ORCID_MEMBER_TYPE = 'ORCID'

  person_id = create_person_id_fk(primary_key=True)
  member_type = Column(String, primary_key=True)
  member_id = Column(String, primary_key=True)

class PersonRole(Base):
  __tablename__ = "person_role"

  person_id = create_person_id_fk(primary_key=True)
  role = Column(String, primary_key=True)

class PersonSubjectArea(Base):
  __tablename__ = "person_subject_area"

  person_id = create_person_id_fk(primary_key=True)
  subject_area = Column(String, primary_key=True)

class Manuscript(Base):
  __tablename__ = "manuscript"

  manuscript_id = Column(String, primary_key=True)
  country = Column(String)
  doi = Column(String)

def create_manuscript_id_fk(**kwargs):
  return Column(
    String,
    ForeignKey('manuscript.manuscript_id', onupdate="CASCADE", ondelete="CASCADE"),
    **kwargs
  )

class ManuscriptVersion(Base):
  __tablename__ = "manuscript_version"

  version_id = Column(String, primary_key=True)
  manuscript_id = create_manuscript_id_fk()
  title = Column(String)
  abstract = Column(String)
  manuscript_type = Column(String)
  decision = Column(String)
  decision_timestamp = Column(DateTime)
  created_timestamp = Column(DateTime)

def create_manuscript_version_id_fk(**kwargs):
  return Column(
    String,
    ForeignKey('manuscript_version.version_id', onupdate="CASCADE", ondelete="CASCADE"),
    **kwargs
  )

class ManuscriptAuthor(Base):
  __tablename__ = "manuscript_author"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)
  seq = Column(Integer)
  is_corresponding_author = Column(Boolean)

class ManuscriptEditor(Base):
  __tablename__ = "manuscript_editor"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)

class ManuscriptSeniorEditor(Base):
  __tablename__ = "manuscript_senior_editor"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)

class ManuscriptReviewer(Base):
  __tablename__ = "manuscript_reviewer"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)

class ManuscriptPotentialEditor(Base):
  __tablename__ = "manuscript_potential_editor"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)

class ManuscriptPotentialReviewer(Base):
  __tablename__ = "manuscript_potential_reviewer"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)
  status = Column(String)
  suggested_to_include = Column(Boolean)
  suggested_to_exclude = Column(Boolean)

class ManuscriptKeyword(Base):
  __tablename__ = "manuscript_keyword"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  keyword = Column(String, primary_key=True)

class ManuscriptSubjectArea(Base):
  __tablename__ = "manuscript_subject_area"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  subject_area = Column(String, primary_key=True)

class ManuscriptResearchOrganism(Base):
  __tablename__ = "manuscript_research_organism"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  research_organism = Column(String, primary_key=True)

class ManuscriptStage(Base):
  __tablename__ = "manuscript_stage"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)
  triggered_by_person_id = create_person_id_fk(nullable=True)
  stage_timestamp = Column(TIMESTAMP, primary_key=True)
  stage_name = Column(String, primary_key=True)

class ManuscriptFunding(Base):
  __tablename__ = "manuscript_funding"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  funder_name = Column(String, primary_key=True)
  grant_reference_number = Column(String, primary_key=True)

class ManuscriptAuthorFunding(Base):
  __tablename__ = "manuscript_author_funding"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  person_id = create_person_id_fk(primary_key=True)
  funder_name = Column(String, primary_key=True)
  grant_reference_number = Column(String, primary_key=True)

# Vector type (Array of floats)
VECTOR = lambda: postgresql.ARRAY(Float).with_variant(PickleType(), 'sqlite')

# generated data for the ML model
class ML_ManuscriptData(Base):
  __tablename__ = "ml_manuscript_data"

  version_id = create_manuscript_version_id_fk(primary_key=True)
  abstract_tokens = Column(String)
  lda_docvec = Column(VECTOR())
  doc2vec_docvec = Column(VECTOR())

class ML_ModelData(Base):
  __tablename__ = "ml_model_data"

  LDA_MODEL_ID = 'lda'
  DOC2VEC_MODEL_ID = 'doc2vec'

  model_id = Column(String, primary_key=True)
  data = Column(LargeBinary)

TABLES = [
  SchemaVersion,
  ImportProcessed,
  Person,
  PersonDatesNotAvailable,
  PersonMembership,
  PersonRole,
  PersonSubjectArea,
  Manuscript,
  ManuscriptVersion,
  ManuscriptAuthor,
  ManuscriptEditor,
  ManuscriptSeniorEditor,
  ManuscriptReviewer,
  ManuscriptPotentialEditor,
  ManuscriptPotentialReviewer,
  ManuscriptKeyword,
  ManuscriptSubjectArea,
  ManuscriptResearchOrganism,
  ManuscriptStage,
  ManuscriptFunding,
  ManuscriptAuthorFunding,
  ML_ManuscriptData,
  ML_ModelData
]
