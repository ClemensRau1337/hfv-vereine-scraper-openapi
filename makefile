.PHONY: lint format test

lint:
	ruff check .
	ruff format --check

format:
	ruff check . --fix
	ruff format

lint-fix:
	ruff check . --fix
	ruff format

test:
	pytest -q
