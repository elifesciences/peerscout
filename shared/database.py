import json
from json import JSONEncoder
import datetime
import configparser

import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import load_only

from .database_schema import (
  Base,
  SCHEMA_VERSION,
  TABLES
)

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj): # pylint: disable=E0202
    try:
      if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    except TypeError:
      pass
    return JSONEncoder.default(self, obj)

def json_serializer(d):
  return json.dumps(d, cls=CustomJSONEncoder)

def db_connect(user, password, db, host='localhost', port=5432):
  '''Returns a connection and a metadata object'''
  # We connect with the help of the PostgreSQL URL
  # postgresql://federer:[email protected]:5432/tennis
  url = 'postgresql://{}:{}@{}:{}/{}'
  url = url.format(user, password, host, port, db)

  # The return value of create_engine() is our connection object
  return sqlalchemy.create_engine(
    url, client_encoding='utf8', json_serializer=json_serializer,
    echo=False
  )

DEFAULT_SCHEMA_VERSION_ID = 'default'

class Entity(object):
  def __init__(self, session, table):
    self.session = session
    self.table = table
    self.auto_commit = False
    inspected = sqlalchemy.inspection.inspect(self.table)
    self.primary_key = inspected.primary_key
    self.relashionships = {
      r.key: r.mapper.class_
      for r in sqlalchemy.inspection.inspect(self.table).relationships
    }

  def _auto_commit_if_enabled(self):
    if self.auto_commit:
      self.session.commit()

  def delete_all(self):
    self.session.query(self.table).delete()
    self._auto_commit_if_enabled()

  def delete_where(self, *conditions):
    self.session.query(self.table).filter(*conditions).delete(synchronize_session=False)
    self._auto_commit_if_enabled()

  def _get_instance(self, *args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0:
      props = args[0]
    else:
      props = kwargs
    # rels = self.relashionships
    # props = dict(props)
    # for k, v in props.items():
    #   if k in rels and isinstance(v, list):
    #     # map relationships to instance of corresponding class
    #     props[k] = [rels[k](**x) for x in v]
    instance = self.table(**props)
    return instance

  def create(self, *args, **kwargs):
    instance = self._get_instance(*args, **kwargs)
    self.session.add(instance)
    self._auto_commit_if_enabled()

  def update(self, *args, **kwargs):
    instance = self._get_instance(*args, **kwargs)
    self.session.merge(instance)
    self._auto_commit_if_enabled()

  def update_or_create(self, *args, **kwargs):
    instance = self._get_instance(*args, **kwargs)
    if self.exists(instance.id):
      self.session.merge(instance)
    else:
      self.session.add(instance)

  def exists(self, entity_id):
    return self.session.query(self.table).filter(
      self.table.id == entity_id
    ).count() > 0

  def get(self, entity_id):
    return self.session.query(self.table).get(entity_id)

  def get_all(self, fields=None):
    q = self.session.query(self.table)
    if fields is not None:
      q = q.options(load_only(*fields))
    return q.all()

  def read_df(self):
    primary_key = self.primary_key
    return pd.read_sql_table(
      self.table.__tablename__,
      self.session.get_bind(),
      index_col=primary_key[0].name if len(primary_key) == 1 else None
    )

  def write_frame(self, df, **kwargs):
    df.to_sql(
      self.table.__tablename__,
      self.session.get_bind(),
      if_exists='append',
      **kwargs
    )

  def count(self):
    return self.session.query(self.table).count()

class Database(object):
  def __init__(self, engine):
    self.engine = engine
    self.session = sessionmaker(engine)()
    self.tables = {
      t.__tablename__: Entity(self.session, t)
      for t in TABLES
    }

  def update_schema(self):
    try:
      version = self.tables['schema_version'].get(DEFAULT_SCHEMA_VERSION_ID)
      if version is not None and version.version == SCHEMA_VERSION:
        Base.metadata.create_all(self.engine)
        return
      else:
        print("schema out of sync, re-creating schema (was: {}, required: {}".format(
          version.version, SCHEMA_VERSION
        ))
    except sqlalchemy.exc.ProgrammingError:
      print("creating schema")
    # the commit is necessary to prevent freezing
    self.commit()
    Base.metadata.drop_all(self.engine)
    Base.metadata.create_all(self.engine)
    self.tables['schema_version'].update_or_create(
      id=DEFAULT_SCHEMA_VERSION_ID,
      version=SCHEMA_VERSION
    )
    self.commit()
    print("done")

  def add(self, entity):
    self.session.add(entity)

  def commit(self):
    self.session.commit()

  def __getitem__(self, name):
    return self.tables[name]

  def __getattr__(self, name):
    return self.tables[name]

def connect_database(*args, **kwargs):
  engine = db_connect(*args, **kwargs)
  return Database(engine)

def connect_configured_database():
  config = configparser.ConfigParser()
  config.read('../app.cfg')
  db_config = config['database']
  name = db_config['name']
  db_host = db_config['db_host']
  db_user = db_config['db_user']
  db_password = db_config['db_password']
  return connect_database(
    db=name,
    host=db_host,
    user=db_user,
    password=db_password
  )
