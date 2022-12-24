#!/bin/bash
#
# deploy mpy fies to the board
#

set -eu

BUILD="./build"
BOARD="/Volumes/CIRCUITPY"

echo "Deploying to $BOARD ..."

if [ -d "$BOARD" ]; then
  cp $BUILD/*.mpy $BOARD
  cp $BUILD/code.py $BOARD
else
  echo "ERROR: Board not mounted at $BOARD"
fi
