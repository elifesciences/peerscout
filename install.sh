#!/bin/bash
set -e # everything must succeed.
echo "[-] install.sh"

maxpy=$(which /usr/bin/python3* | grep -E '[0-9]$' | sort -r | head -n 1)

py=${maxpy##*/} # magic

# check for exact version of python3
if [ ! -e "venv/bin/$py" ]; then
    echo "could not find venv/bin/$py, recreating venv"
    rm -rf venv
    virtualenv --python="$maxpy" venv
fi

source venv/bin/activate

pip install -r requirements.spacy.txt
pip install -r requirements.prereq.txt
pip install -r requirements.txt

if [ "${DEBUG:-1}" = "1" ]; then
    pip install -r requirements.dev.txt
fi

python -m spacy download en

echo "[✓] install.sh"
