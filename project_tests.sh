#!/bin/bash
set -e # everything must succeed.

source venv/bin/activate

pytest

cd client
npm test
