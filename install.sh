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

# we need to install packages in the correct order to avoid module not found
for line in $(cat requirements.txt)
do
  pip install $line
done

echo "[✓] install.sh"
