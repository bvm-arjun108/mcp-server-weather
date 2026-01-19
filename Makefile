PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: venv install run-dev test clean

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

run-dev:
	$(BIN)/mcp dev server.py

test:
	$(BIN)/python test_tools.py

clean:
	rm -rf $(VENV)
