# Layered Architecture with FastAPI

This project demonstrates a clean, layered architecture implementation using FastAPI, featuring a pizza and beer ordering system. It showcases best practices for building maintainable, testable, and scalable applications.

## Features

- Clean, layered architecture
- Async service interfaces
- Dependency injection
- DTO-based validation
- Multiple entrypoints (API, CLI, Celery)
- Comprehensive testing strategy

## Project Structure

```
src/
├── api/            # FastAPI endpoints
├── cli/            # Typer CLI commands
├── core/           # Core domain logic
├── dto/            # Data Transfer Objects
├── services/       # Service interfaces and implementations
├── repositories/   # Data access layer
└── config/         # Configuration management
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### API Server
```bash
uvicorn src.api.main:app --reload
```

### CLI
```bash
python -m src.cli.main
```

### Celery Worker
```bash
celery -A src.workers.main worker --loglevel=info
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src tests
isort src tests
```

### Type Checking
```bash
mypy src
```

## Documentation

- API documentation is available at `/docs` when running the server
- Architecture documentation is in the `docs/` directory
- Presentation slides can be generated using Marp (see docs/presentation.md)

## License

MIT
