#!/bin/bash

set -e

INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$INSTALL_DIR"

"$INSTALL_DIR/venv/bin/python" -m peerscout.preprocessing.migrateSchema
