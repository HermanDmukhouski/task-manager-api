.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: help install dev test lint typecheck format check pre-commit up down logs migrate makemigrations

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and pre-commit hooks
	poetry install
	poetry run pre-commit install

dev: ## Run the API with autoreload
	@set -a && [ -f .env ] && . ./.env; set +a; \
	poetry run uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port $${APP_PORT:-8000}

test: ## Run the test suite
	poetry run pytest

lint: ## Run ruff linter
	poetry run ruff check src tests

format: ## Format code with ruff
	poetry run ruff format src tests
	poetry run ruff check --fix src tests

typecheck: ## Run mypy
	poetry run mypy src

check: lint typecheck test ## Run lint, typecheck and tests

pre-commit: ## Run all pre-commit hooks
	poetry run pre-commit run --all-files

up: ## Start PostgreSQL via Docker Compose
	docker compose up -d

down: ## Stop PostgreSQL containers
	docker compose down

logs: ## Tail PostgreSQL logs
	docker compose logs -f postgres

migrate: ## Apply database migrations
	poetry run alembic upgrade head

makemigrations: ## Autogenerate a migration (make makemigrations msg="...")
	@test -n "$(msg)" || (echo 'Usage: make makemigrations msg="description"' && exit 1)
	poetry run alembic revision --autogenerate -m "$(msg)"
