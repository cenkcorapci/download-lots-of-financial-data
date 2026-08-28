.PHONY: help install download-all verify clean

PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

help:
	@echo "Targets:"
	@echo "  make install       - create venv and install dependencies"
	@echo "  make download-all  - download all financial datasets"
	@echo "  make verify        - verify dataset integrity (>=30 datasets)"
	@echo "  make clean         - remove downloaded datasets"

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

download-all: install
	$(PY) scripts/download_all.py

verify:
	$(PY) scripts/verify_datasets.py

clean:
	rm -rf datasets/
