import pandas as pd

from .lda_utils import train_lda


class TestTrainLda:
    def test_should_not_fail(self):
        assert train_lda(pd.Series(['word1 word2'] * 10), min_df=1, max_df=1.0)
