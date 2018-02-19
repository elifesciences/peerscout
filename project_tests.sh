#!/bin/bash
set -e # everything must succeed.

source venv/bin/activate

pytest --cov=peerscout --cov-report html:build/cov_html  --junitxml=build/pytest.xml

cd client
npm test
cd ..

# run proofreader (pylint and flake8) informational only
python -m proofreader peerscout || true
