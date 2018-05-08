PKGNAME=ducroy

default: build

build: 
	@echo "No need to build :)"

install: 
	pip install ".[full]"

install-dev: dev-dependencies
	pip install -e ".[full]"

clean:
	python setup.py clean --all

test: 
	py.test --junitxml=./junit.xml ducroy || true

test-cov:
	py.test --cov ./ --cov-report term-missing --cov-report xml ducroy || true

test-loop: 
	py.test || true
	ptw --ext=.py,.pyx

flake8: 
	py.test --flake8 || true

pep8: flake8

docstyle: 
	py.test --docstyle  || true

lint: 
	py.test --pylint || true

dependencies:
	pip install -Ur requirements.txt

dev-dependencies:
	pip install -Ur dev-requirements.txt

.PHONY: clean build install test test-nocov flake8 pep8 dependencies dev-dependencies
