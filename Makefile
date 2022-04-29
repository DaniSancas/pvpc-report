.PHONY: install test

default: install

install:
	pipenv install --dev

test:
	pipenv run test -v
