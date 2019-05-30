#!/bin/bash
set -e # everything must succeed.

source venv/bin/activate

echo "running flake8"
flake8 peerscout tests setup.py

echo "running pylint"
pylint peerscout tests setup.py

echo "running tests"
pytest --cov=peerscout --cov-report html:build/cov_html --cov-report xml:build/cov.xml --junitxml=build/pytest.xml
