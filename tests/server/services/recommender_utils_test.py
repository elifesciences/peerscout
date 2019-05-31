from peerscout.server.services.recommender_utils import (
    sorted_manuscript_scores_descending
)


class TestSortedManuscriptScoresDescending:
    def test_should_return_empty_list_for_empty_list(self):
        assert sorted_manuscript_scores_descending([]) == []

    def test_should_return_sort_by_combined_score_first(self):
        scores = [{
            'combined': 0.1,
            'keyword': 0.2,
            'similarity': 0.2
        }, {
            'combined': 0.2,
            'keyword': 0.1,
            'similarity': 0.1
        }]
        assert sorted_manuscript_scores_descending(scores) == [
            scores[1], scores[0]
        ]

    def test_should_return_sort_by_keyword_score_second(self):
        scores = [{
            'combined': 0.5,
            'keyword': 0.1,
            'similarity': 0.2
        }, {
            'combined': 0.5,
            'keyword': 0.2,
            'similarity': 0.1
        }]
        assert sorted_manuscript_scores_descending(scores) == [
            scores[1], scores[0]
        ]

    def test_should_return_sort_by_similarity_score_last(self):
        scores = [{
            'combined': 0.5,
            'keyword': 0.5,
            'similarity': 0.1
        }, {
            'combined': 0.5,
            'keyword': 0.5,
            'similarity': 0.2
        }]
        assert sorted_manuscript_scores_descending(scores) == [
            scores[1], scores[0]
        ]

    def test_should_treat_none_as_zero(self):
        scores = [{
            'combined': None,
            'keyword': None,
            'similarity': None
        }, {
            'combined': 0.0,
            'keyword': 0.0,
            'similarity': 0.1
        }]
        assert sorted_manuscript_scores_descending(scores) == [
            scores[1], scores[0]
        ]
