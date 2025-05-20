# Help generator
help: ## Display this help.
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install-marp: ## Install marp-cli
	npm install -g @marp-team/marp-cli

create-presentation: install-marp ## Generate presentation PDF
	marp docs/presentation.md --pdf

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | cut -d ':' -f 1)

run: sync up ## Run the FastAPI application
	uv run uvicorn src.layered_architecture.main:app --reload --host 0.0.0.0 --port 8000

down: ## Stop all containers
	docker compose down

up: ## Start all containers
	docker compose up -d

create-migrations: ## Create new database migrations
	cd src && uv run alembic -c layered_architecture/db/alembic/alembic.ini revision --autogenerate

migrate: ## Apply database migrations
	cd src && uv run alembic -c layered_architecture/db/alembic/alembic.ini upgrade head

install-pre-commit: ## Install pre-commit hooks
	pre-commit install

sync: ## Sync the project
	uv sync

dbshell: ## Open PSQL shell
	docker compose exec postgres psql -U postgres -d layered_arch
