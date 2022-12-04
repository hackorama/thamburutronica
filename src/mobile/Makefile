#
# build: make help
#

help:	## Show help
		@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

deps:	## Install python packages
		python3 -m pip install --upgrade pip
		pip3 install -r requirements.txt
		pip3 install -r dev.requirements.txt

check:	## Run python code checks
		isort .
		black .
		pylint *.py
		mypy *.py

build:	## Build typescript
		tsc --strict

all:	## Check and build
all: check build
