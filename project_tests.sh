#!/bin/bash
set -e # everything must succeed.

source venv/bin/activate

cd server
pytest

cd ../preprocessing
pytest
