#!/bin/bash
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$INSTALL_DIR/preprocessing"
"$INSTALL_DIR/venv/bin/python" ./updateDataAndReload.py
