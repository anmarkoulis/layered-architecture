# Help generator
help: ## Display this help.
	@echo "Please use 'make <target>' where <target> is one of the following:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install-uv: ## Install uv package manager
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Installing uv package manager..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "uv is already installed"; \
	fi

install-marp: ## Install marp-cli
	npm install -g @marp-team/marp-cli

install-mermaid-cli: ## Install mermaid-cli
	npm install -g @mermaid-js/mermaid-cli

create-presentation: install-marp generate-diagrams ## Generate presentation PDF
	marp docs/presentation.md --pdf --allow-local-files

run: install-uv sync up ## Run the FastAPI application
	PYTHONDONTWRITEBYTECODE=1 uv run uvicorn src.layered_architecture.main:app --reload --host 0.0.0.0 --port 8000

down: ## Stop all containers
	docker compose down

down-volumes: ## Stop all containers and remove volumes
	docker compose down -v

up: ## Start all containers
	docker compose up -d

create-migrations: install-uv ## Create new database migrations
	cd src && uv run alembic -c layered_architecture/db/alembic/alembic.ini revision --autogenerate

migrate: install-uv ## Apply database migrations
	cd src && uv run alembic -c layered_architecture/db/alembic/alembic.ini upgrade head

install-pre-commit: ## Install pre-commit hooks
	pre-commit install

sync: install-uv ## Sync the project
	uv sync

dbshell: ## Open PSQL shell
	docker compose exec postgres psql -U postgres -d layered_arch

test: ## Run tests
	PYTHONPATH=src uv run pytest tests --cov --cov-report=term --cov-report=html --cov-report=xml --cov-report=json ${args}

generate-diagrams: install-mermaid-cli ## Generate diagrams
	@echo "Generating diagrams..."
	@for file in docs/diagrams/source/*.mmd; do \
		filename=$$(basename $$file .mmd); \
		mmdc -i $$file -o docs/diagrams/generated/$$filename.png; \
	done
	@echo "Diagrams generated successfully!"

clean-pyc: ## Remove Python cache files
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | cut -d ':' -f 1)
