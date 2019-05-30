import logging

import pandas as pd
import sqlalchemy

from ..docvec_model import SpacyTransformer, DocvecModelUtils
from ..docvec_model.lda_utils import train_lda

from ..shared.database import connect_managed_configured_database

NAME = 'generateLdaDocVec'


def process_article_abstracts(db, n_topics=10):
    # We need to either:
    # a) train the LDA model on all of the data (not just new ones)
    #    Pros: all of the data is considered
    # b) or use a pre-trained model to predict the values for new entries
    #    Pros: Faster; Vectors are more stable

    # Option a) is implemented below

    logger = logging.getLogger(NAME)

    ml_manuscript_data_table = db['ml_manuscript_data']

    # Find out whether we need to update anything at all
    ml_data_requiring_lda_docvec_count = db.session.query(
        ml_manuscript_data_table.table
    ).filter(
        sqlalchemy.and_(
            ml_manuscript_data_table.table.abstract_tokens != None,
            ml_manuscript_data_table.table.lda_docvec == None,  # pylint: disable=C0121
        )
    ).count()

    if ml_data_requiring_lda_docvec_count > 0:
        # Yes, get all of the data
        logger.info(
            "number of new manuscript versions requiring LDA document vectors: %d",
            ml_data_requiring_lda_docvec_count
        )
        ml_data_requiring_lda_docvec_df = pd.DataFrame(db.session.query(
            ml_manuscript_data_table.table.version_id,
            ml_manuscript_data_table.table.abstract_tokens
        ).filter(
            sqlalchemy.and_(
                ml_manuscript_data_table.table.abstract_tokens != None
            )
        ).all(), columns=['version_id', 'abstract_tokens'])
    else:
        ml_data_requiring_lda_docvec_df = pd.DataFrame([])

    logger.info(
        "number of manuscript versions requiring LDA document vectors: %d",
        len(ml_data_requiring_lda_docvec_df)
    )

    if len(ml_data_requiring_lda_docvec_df) > 0:
        texts = ml_data_requiring_lda_docvec_df['abstract_tokens'].values
        lda_result = train_lda(texts, n_topics=n_topics)
        docvecs = lda_result.docvecs

        predict_model = DocvecModelUtils.create_lda_predict_model(
            spacy_transformer=SpacyTransformer(),
            vectorizer=lda_result.vectorizer,
            lda=lda_result.lda
        )
        predict_model_binary = DocvecModelUtils.save_predict_model_to_binary(predict_model)

        ml_data_df = ml_data_requiring_lda_docvec_df[['version_id']]
        ml_data_df['lda_docvec'] = docvecs
        ml_manuscript_data_table.update_list(
            ml_data_df.to_dict(orient='records')
        )

        ml_model_data_table = db['ml_model_data']
        ml_model_data_table.update_or_create(
            model_id=ml_model_data_table.table.LDA_MODEL_ID,
            data=predict_model_binary
        )

        db.commit()


N_TOPICS = 20


def main():
    with connect_managed_configured_database() as db:

        process_article_abstracts(db)


if __name__ == "__main__":
    from ..shared.logging_config import configure_logging
    configure_logging('update')

    main()
