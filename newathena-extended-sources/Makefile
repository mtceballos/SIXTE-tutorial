.PHONY: check quality lint format format-check test typecheck build audit-tree phase1-readiness

check: test build audit-tree

quality: lint format-check typecheck

lint:
	python -m ruff check src tests scripts

format:
	python -m ruff format src tests scripts

format-check:
	python -m ruff format --check src tests scripts

typecheck:
	python -m mypy src

test:
	python -m pytest

build:
	python -m build

audit-tree:
	python scripts/validate_workspace.py

phase1-readiness:
	python scripts/check_phase1_readiness.py
