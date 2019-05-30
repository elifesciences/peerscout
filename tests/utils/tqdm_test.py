from unittest.mock import patch, MagicMock

import pytest

from peerscout.utils import tqdm as tqdm_module
from peerscout.utils.tqdm import tqdm, MIN_INTERVAL_KEY, DEFAULT_NON_ATTY_MIN_INTERVAL

ARGS = ['arg1', 'arg2']
KW_ARGS = {'key1': 'value1', 'key2': 'value2'}

OTHER_MIN_INTERVAL = 123.4

DESCRIPTION = 'description'


@pytest.fixture(name='tqdm_mock', autouse=True)
def _tqdm_mock():
    with patch.object(tqdm_module, '_tqdm') as tqdm_mock:
        yield tqdm_mock


@pytest.fixture(name='isatty_mock', autouse=True)
def _isatty_mock():
    with patch('sys.stderr.isatty') as isatty_mock:
        yield isatty_mock


@pytest.fixture(name='env_get_mock', autouse=True)
def _env_get_mock():
    with patch('os.environ.get') as env_get_mock:
        env_get_mock.return_value = None
        yield env_get_mock


class TestTqdm:
    def test_should_not_set_min_interval_if_terminal(
            self, tqdm_mock: MagicMock, isatty_mock: MagicMock):

        isatty_mock.return_value = True
        tqdm(*ARGS, **KW_ARGS)
        tqdm_mock.assert_called_with(
            *ARGS, **KW_ARGS
        )

    def test_should_use_default_non_atty_min_interval_if_not_terminal(
            self, tqdm_mock: MagicMock, isatty_mock: MagicMock):

        isatty_mock.return_value = False
        tqdm(*ARGS, **KW_ARGS)
        tqdm_mock.assert_called_with(
            *ARGS, mininterval=DEFAULT_NON_ATTY_MIN_INTERVAL, **KW_ARGS
        )

    def test_should_use_min_interval_from_env(
            self, tqdm_mock: MagicMock, env_get_mock: MagicMock):

        env_get_mock.return_value = OTHER_MIN_INTERVAL
        tqdm(*ARGS, **KW_ARGS)
        tqdm_mock.assert_called_with(
            *ARGS, mininterval=OTHER_MIN_INTERVAL, **KW_ARGS
        )
        env_get_mock.assert_called_with(MIN_INTERVAL_KEY)

    def test_should_not_pass_when_updating_description_and_in_terminal(
            self, tqdm_mock: MagicMock, isatty_mock: MagicMock):

        isatty_mock.return_value = True
        set_description_mock = tqdm_mock.return_value.set_description
        tqdm(*ARGS, **KW_ARGS).set_description(DESCRIPTION)
        set_description_mock.assert_called_with(
            DESCRIPTION
        )

    def test_should_pass_refresh_false_when_updating_description_and_not_terminal(
            self, tqdm_mock: MagicMock, isatty_mock: MagicMock):

        isatty_mock.return_value = False
        set_description_mock = tqdm_mock.return_value.set_description
        tqdm(*ARGS, **KW_ARGS).set_description(DESCRIPTION)
        set_description_mock.assert_called_with(
            DESCRIPTION, refresh=False
        )

    def test_should_be_able_to_call_tqdm_pandas(
            self, tqdm_mock: MagicMock):

        tqdm.pandas()
        tqdm_mock.pandas.assert_called()
