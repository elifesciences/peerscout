#!/bin/bash

set -e

INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$INSTALL_DIR/server"

exec "$INSTALL_DIR/venv/bin/python" ./server.py
