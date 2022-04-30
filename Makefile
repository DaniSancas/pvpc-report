.PHONY: install install-dev test format precommit

default: install

install:
	pipenv install

install-dev:
	pipenv install --dev

test:
	pipenv run test -vv --cov=pvpc --cov-report=term-missing --cov-branch

format:
	pipenv run black pvpc tests

precommit: format test
