#!/bin/bash
set -e # everything must succeed.

source venv/bin/activate

pytest --cov=peerscout --cov-report html:build/cov_html --cov-report xml:build/cov.xml --junitxml=build/pytest.xml

# run proofreader (pylint and flake8) informational only
python -m proofreader peerscout || true
