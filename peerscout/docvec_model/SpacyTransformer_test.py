from .SpacyTransformer import SpacyTransformer


def strip_all(l):
    return [s.strip() for s in l]


class TestSpacyTransformer:
    def test_should_not_fit(self):
        SpacyTransformer().fit(self, ['dummy'])

    def test_should_extract_nouns_and_add_pos_tag(self):
        assert (
            strip_all(SpacyTransformer().transform(['manuscript'])) ==
            ['manuscript|NOUN']
        )

    def test_should_extract_proper_nouns_and_add_pos_tag(self):
        assert (
            strip_all(SpacyTransformer().transform(['Jupiter'])) ==
            ['jupiter|PROPN']
        )

    def test_should_extract_single_adjective_of_noun_and_also_combine_to_single_token(self):
        assert (
            strip_all(SpacyTransformer().transform(['good manuscript'])) ==
            ['good|ADJ manuscript|NOUN good_manuscript|NOUN']
        )

    def test_should_ignore_verbs(self):
        assert (
            strip_all(SpacyTransformer().transform(['writting a manuscript'])) ==
            ['manuscript|NOUN']
        )

    def test_should_extract_using_pipe(self):
        assert strip_all(SpacyTransformer(
            use_pipe=True, use_progress=False
        ).transform(['manuscript'])) == ['manuscript|NOUN']

    def test_should_extract_without_pipe(self):
        assert strip_all(SpacyTransformer(
            use_pipe=False, use_progress=False
        ).transform(['manuscript'])) == ['manuscript|NOUN']

    def test_should_extract_using_progress(self):
        assert strip_all(SpacyTransformer(
            use_progress=True
        ).transform(['manuscript'])) == ['manuscript|NOUN']
