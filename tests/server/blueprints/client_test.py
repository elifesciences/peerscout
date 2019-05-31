from __future__ import absolute_import

import logging
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from flask import Flask

from peerscout.server.blueprints import client as client_module
from peerscout.server.blueprints.client import create_client_blueprint

LOGGER = logging.getLogger(__name__)


@pytest.fixture(name='temp_client_folder', autouse=True)
def _temp_client_folder(tmpdir):
    temp_client_folder = str(tmpdir)
    with patch.object(client_module, 'get_client_folder', lambda: temp_client_folder):
        yield tmpdir


@contextmanager
def _client_test_client():
    blueprint = create_client_blueprint()
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    yield app.test_client()


@pytest.mark.slow
class TestClientBlueprint:
    class TestIndex:
        def test_should_return_no_cache_headers_for_index(self, temp_client_folder):
            with _client_test_client() as test_client:
                temp_client_folder.join('index.html').write('content')
                response = test_client.get('/')
                assert response.status_code == 200
                assert response.headers['Cache-Control'] == 'no-cache, no-store, must-revalidate'
                assert response.headers['Pragma'] == 'no-cache'

        def test_should_return_regular_cache_headers_for_bundle(self, temp_client_folder):
            with _client_test_client() as test_client:
                temp_client_folder.join('bundle.js').write('content')
                response = test_client.get('/bundle.js')
                assert response.status_code == 200
                assert response.headers['Cache-Control'] == 'public, max-age=43200'
