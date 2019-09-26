import logging
from pathlib import Path

import pytest
from py._path.local import LocalPath


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logging.root.handlers = []
    logging.basicConfig(level='INFO')
    logging.getLogger('tests').setLevel('DEBUG')
    logging.getLogger('peerscout').setLevel('DEBUG')


@pytest.fixture
def temp_dir(tmpdir: LocalPath):
    # convert to standard Path
    return Path(str(tmpdir))
