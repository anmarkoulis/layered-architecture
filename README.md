# Layered Architecture & Dependency Injection Example

This project serves as a practical example for the Athens Python Meetup presentation on "Layered Architecture & Dependency Injection: A Recipe for Clean and Testable FastAPI Code". It demonstrates how to structure a FastAPI application using layered architecture principles and dependency injection.

## Project Structure

The project follows a layered architecture pattern with clear separation of concerns:

```
src/layered_architecture/
├── api/                    # Presentation Layer (FastAPI routes)
├── services/              # Service Layer (Business Logic)
│   ├── interfaces/        # Service interfaces
│   └── concrete/          # Service implementations
├── dao/                   # Data Access Layer
│   ├── interfaces/        # DAO interfaces
│   └── concrete/          # DAO implementations
├── dto/                   # Data Transfer Objects
├── db/                    # Database models and migrations
└── config/               # Application configuration
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Node.js (for generating diagrams and presentation)

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/layered-architecture.git
cd layered-architecture
```

2. Start the application:
```bash
make run
```

The application will be available at `http://localhost:8000`

## Available Commands

To see all available commands and their descriptions:
```bash
make help
```

## Documentation

To generate the presentation that explains the architecture and design decisions:
```bash
make create-presentation
```

## Key Features

- Layered Architecture implementation
- Dependency Injection using FastAPI's dependency system
- Async SQLAlchemy for database operations
- Comprehensive test suite
- Docker-based development environment
- Database migrations with Alembic

## API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
