#
# Please run: make help
#

help:	    ## Show help
		@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

deps:	    ## Install dev python packages
		test -d venv || python3 -m venv venv
		. venv/bin/activate && which python3 && python3 -m pip install --upgrade pip && pip3 -q install -r dev.requirements.txt

device:	    ## Install circuitpython packages on device
device: deps
		circup install

check:	    ## Run python code checks
check: deps
		. venv/bin/activate && isort . &&  black . &&  pylint *.py && mypy --explicit-package-bases  *.py && cd ../ && lint-imports --config ./microcontroller/.importlinter && cd -

tests:	    ## Run tests
tests: check
		. venv/bin/activate && python3 tests.py

compile:    ## Build mpy files
compile: check
		./build.sh

deploy:	    ## Deploy mpy files to device
deploy: compile
		./deploy.sh
