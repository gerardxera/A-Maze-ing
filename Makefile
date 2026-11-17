VENV_BIN := $(shell if [ -d .venv/bin ]; then echo .venv/bin/; fi)
PYTHON   := $(VENV_BIN)python3
PIP      := $(VENV_BIN)pip
CONFIG   := config.txt

.PHONY: install run debug clean lint lint-strict build

install:
	$(PIP) install --upgrade pip
	$(PIP) install pydantic flake8 mypy build

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

build:
	$(PYTHON) -m build
	cp dist/mazegen-*.whl .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist *.egg-info

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict
