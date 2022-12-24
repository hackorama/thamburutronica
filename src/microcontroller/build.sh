#!/bin/bash
#
# compile mpy files to deploy to the board
#

set -eu

BUILD="./build"

echo "Cross compiling mpy files in $BUILD ..."

for f in `ls *.py`
do
  echo $f
  mpy-cross $f
done

mkdir -p $BUILD
mv *.mpy ./$BUILD
rm ./$BUILD/code.mpy
rm ./$BUILD/tests.mpy
cp code.py ./$BUILD
