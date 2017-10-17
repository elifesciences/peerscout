import json
from json import JSONEncoder
import datetime
import logging
from contextlib import contextmanager

import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import load_only

from .database_schema import (
  Base,
  SCHEMA_VERSION,
  TABLES
)

from .database_views import create_views

from .app_config import get_app_config

NAME = 'database'

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

  def _assert_single_primary_key(self):
    if len(self.primary_key) != 1:
      raise Exception("operation only supported for simple primary key, but found: {}".format(
        self.primary_key
      ))

  def _get_single_primary_key_name(self):
    self._assert_single_primary_key()
    return self.primary_key[0].name

  def _get_single_primary_key_field(self):
    return getattr(self.table, self._get_single_primary_key_name())

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
    id_name = self._get_single_primary_key_name()
    instance = self._get_instance(*args, **kwargs)
    if self.exists(getattr(instance, id_name)):
      self.session.merge(instance)
    else:
      self.session.add(instance)

  def create_list(self, objs):
    self.session.bulk_insert_mappings(self.table, objs)

  def update_list(self, objs):
    self.session.bulk_update_mappings(self.table, objs)

  def update_or_create_list(self, objs):
    if len(self.primary_key) != 1:
      raise Exception("operation only supported for simple primary key, but found: {}".format(
        self.primary_key
      ))
    id_attr = self.primary_key[0].name
    obj_ids = [o.get(id_attr) for o in objs]
    existing_ids = set(self.get_existing_ids(obj_ids))
    existing_objs = [o for obj_id, o in zip(obj_ids, objs) if obj_id in existing_ids]
    not_existing_objs = [o for obj_id, o in zip(obj_ids, objs) if obj_id not in existing_ids]
    if len(existing_objs) > 0:
      self.update_list(existing_objs)
    if len(not_existing_objs) > 0:
      self.create_list(not_existing_objs)

  def exists(self, entity_id):
    id_field = self._get_single_primary_key_field()
    return self.session.query(self.table).filter(
      id_field == entity_id
    ).count() > 0

  def get(self, entity_id):
    return self.session.query(self.table).get(entity_id)

  def get_all(self, fields=None):
    q = self.session.query(self.table)
    if fields is not None:
      q = q.options(load_only(*fields))
    return q.all()

  def get_existing_ids(self, ids):
    id_field = self._get_single_primary_key_field()
    return set([x[0] for x in self.session.query(
      id_field
    ).filter(
      id_field.in_(ids)
    ).all()])

  def read_frame(self):
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
    self.logger = logging.getLogger(NAME)
    self.engine = engine
    self.session = sessionmaker(engine)()
    self.views = create_views(engine.dialect.name)
    self.tables = {
      t.__tablename__: Entity(self.session, t)
      for t in TABLES + self.views
    }

  def get_current_schema_version(self):
    try:
      version = self.tables['schema_version'].get(DEFAULT_SCHEMA_VERSION_ID)
      return version
    except sqlalchemy.exc.ProgrammingError:
      return None
    except sqlalchemy.exc.OperationalError:
      return None

  def drop_views(self):
    for view in reversed(self.views):
      self.engine.execute('DROP VIEW IF EXISTS {}'.format(
        view.__tablename__
      ))
    self.commit()

  def create_views(self):
    for view in self.views:
      self.logger.info('creating view %s', view.__tablename__)
      self.engine.execute('CREATE VIEW {} AS {}'.format(
        view.__tablename__,
        view.__query__
      ))
    self.commit()

  def _shallow_migrate_schema(self):
    self.logger.info('shallow migrate schema (no data modification)')
    Base.metadata.create_all(self.engine)
    self.drop_views()
    self.create_views()

  def _full_migrate_schema(self):
    self.drop_views()
    # the commit is necessary to prevent freezing
    self.commit()
    Base.metadata.drop_all(self.engine)
    Base.metadata.create_all(self.engine)
    self.create_views()

    self.tables['schema_version'].update_or_create(
      schema_version_id=DEFAULT_SCHEMA_VERSION_ID,
      version=SCHEMA_VERSION
    )
    self.commit()

  def update_schema(self):
    version = self.get_current_schema_version()
    if version is not None and version.version == SCHEMA_VERSION:
      self._shallow_migrate_schema()
    else:
      if version is None:
        self.logger.info("creating schema")
      else:
        self.logger.info(
          "schema out of sync, re-creating schema (was: %s, required: %s)",
          version.version if version else None, SCHEMA_VERSION
        )
      self._full_migrate_schema()
      self.logger.info("done")

  def sorted_table_names(self):
    return [t.name for t in Base.metadata.sorted_tables]

  def add(self, entity):
    self.session.add(entity)

  def commit(self):
    self.session.commit()

  def close(self):
    self.session.close()

  def __getitem__(self, name):
    return self.tables[name]

  def __getattr__(self, name):
    return self.tables[name]

def connect_database(*args, **kwargs):
  engine = db_connect(*args, **kwargs)
  return Database(engine)

def connect_configured_database():
  config = get_app_config()
  db_config = config['database']
  name = db_config['name']
  if name.startswith('sqlite:'):
    return Database(sqlalchemy.create_engine(name, echo=False))
  db_host = db_config['host']
  db_port = db_config['port']
  db_user = db_config['user']
  db_password = db_config['password']
  return connect_database(
    db=name,
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password
  )

@contextmanager
def connect_managed_configured_database():
  db = connect_configured_database()
  yield db
  db.close()
