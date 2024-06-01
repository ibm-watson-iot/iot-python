.PHONY: docs install test build clean

venv:
	python3 -m venv venv

clean:
	rm -rf venv

install: venv
	. venv/bin/activate && python -m pip install --editable .[dev]

test: venv
	. venv/bin/activate && pytest

build: venv
	rm README.rst
	. venv/bin/activate && python -m build

docs:
	cd docs && make html
