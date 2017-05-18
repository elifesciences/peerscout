import logging

import pandas as pd
from tqdm import tqdm
import sqlalchemy

from docvec_model_proxy import SpacyTransformer # pylint: disable=E0611

from convertUtils import unescape_and_strip_tags_if_not_none

from shared_proxy import database

NAME = 'generateTextTokens'

def process_manuscript_versions(
  db, extract_keywords_from_list):

  logger = logging.getLogger(NAME)

  ml_manuscript_data_table = db['ml_manuscript_data']
  manuscript_version_table = db['manuscript_version']

  version_ids_with_abstract_tokens_query = db.session.query(
    ml_manuscript_data_table.table.version_id
  ).filter(
    ml_manuscript_data_table.table.abstract_tokens != None
  )
  versions_requiring_tokens_df = pd.DataFrame(db.session.query(
    manuscript_version_table.table.version_id,
    manuscript_version_table.table.abstract
  ).filter(
    sqlalchemy.and_(
      ~manuscript_version_table.table.version_id.in_(version_ids_with_abstract_tokens_query),
      manuscript_version_table.table.abstract != None
    )
  ).all(), columns=['version_id', 'abstract'])
  logger.debug(
    "number of manuscript versions requiring tokens: %d", len(versions_requiring_tokens_df)
  )

  if len(versions_requiring_tokens_df) > 0:
    ml_data_df = versions_requiring_tokens_df[['version_id']]
    ml_data_df['abstract_tokens'] = (
      extract_keywords_from_list(versions_requiring_tokens_df['abstract'])
    )
    ml_manuscript_data_table.update_or_create_list(
      ml_data_df.to_dict(orient='records')
    )

    db.commit()

def main():
  tqdm.pandas()

  spacy_transformer = SpacyTransformer(use_pipe=True, use_progress=True)

  def extract_keywords_from_list(texts):
    return spacy_transformer.transform([
      unescape_and_strip_tags_if_not_none(s)
      for s in texts
    ])

  db = database.connect_configured_database()

  process_manuscript_versions(db, extract_keywords_from_list)

if __name__ == "__main__":
  from shared_proxy import configure_logging
  configure_logging()

  main()
