SHELL := /bin/bash

# ===== Config =====

IMAGE ?= hfv-vereine-scraper-api:latest
CONTAINER ?= hfv-vereine-scraper-api

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

# ===== Docker =====
.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE) .

.PHONY: docker-run
docker-run:
	docker run --rm -p 8000:8000 --name $(CONTAINER) $(IMAGE)