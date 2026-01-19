set shell := ["/bin/bash", "-cu"]

python := "python3"
venv := ".venv"

venv:
  {{python}} -m venv {{venv}}

install: venv
  {{venv}}/bin/python -m pip install --upgrade pip
  {{venv}}/bin/pip install -r requirements.txt

run-dev:
  {{venv}}/bin/mcp dev server.py

test:
  {{venv}}/bin/python test_tools.py

clean:
  rm -rf {{venv}}
