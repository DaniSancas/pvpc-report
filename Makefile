.PHONY: install test

default: install

install:
	pipenv install --dev

test:
	pipenv run test -vv --cov=pvpc --cov-report=term-missing --cov-branch

format:
	pipenv run black pvpc tests

precommit: format test
