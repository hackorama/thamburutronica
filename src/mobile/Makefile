#
# Please run: make help
#

help:	## Show help
		@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

deps:	## Install python packages
		test -d venv || python3 -m venv venv
		. venv/bin/activate && which python3 && python3 -m pip install --upgrade pip && pip3 -q install -r dev.requirements.txt && mypy --install-types

check:	## Run python code checks
check: deps
		. venv/bin/activate && isort . &&  black . &&  pylint *.py && mypy *.py

build:	## Build typescript
build: check
		tsc --strict

deploy:	## Run the server
deploy: build
		./server.sh

