from __future__ import absolute_import

import pandas as pd

from peerscout.utils.pandas import (
    groupby_agg_droplevel
)


class TestGroupbyAggDroplevel:
    def test_should_apply_simple_aggregation_with_function_name(self):
        df = pd.DataFrame({
            'g': ['g1', 'g1', 'g2'],
            'v': [1, 2, 3]
        })
        result_df = groupby_agg_droplevel(df, ['g'], {
            'v': 'sum'
        })
        assert list(result_df.columns) == ['g', 'v']
        assert list(result_df.values.tolist()) == [
            ['g1', 3],
            ['g2', 3]
        ]

    def test_should_apply_simple_aggregation_with_function(self):
        df = pd.DataFrame({
            'g': ['g1', 'g1', 'g2'],
            'v': [1, 2, 3]
        })
        result_df = groupby_agg_droplevel(df, ['g'], {
            'v': sum
        })
        assert list(result_df.columns) == ['g', 'v']
        assert list(result_df.values.tolist()) == [
            ['g1', 3],
            ['g2', 3]
        ]

    def test_should_apply_nested_aggregation_with_functions(self):
        df = pd.DataFrame({
            'group': ['g1', 'g1', 'g2'],
            'value': [1, 2, 3]
        })
        result_df = groupby_agg_droplevel(df, ['group'], {
            'value': {
                'sum': sum,
                'count': pd.np.size
            }
        })
        assert set(result_df.columns) == {'group', 'sum', 'count'}
        # ensure the order of the columns is as expected
        result_df = result_df[['group', 'sum', 'count']]
        assert result_df.values.tolist() == [
            ['g1', 3, 2],
            ['g2', 3, 1]
        ]

    def test_should_include_columns_also_for_empty_dataframe(self):
        df = pd.DataFrame({
            'group': [],
            'value': []
        })
        result_df = groupby_agg_droplevel(df, ['group'], {
            'value': {
                'sum': sum,
                'count': pd.np.size
            }
        })
        assert set(result_df.columns) == {'group', 'sum', 'count'}
        assert len(result_df) == 0
