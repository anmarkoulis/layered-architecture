---
marp: true
theme: beam
class: invert
paginate: true
header: "Athens Python Meetup"
footer: "Layered Architecture & Dependency Injection"
style: |
  section {
    font-size: 1.5em;
    background-color: #1E1E1E;
    color: #E0E0E0;
  }
  h1 {
    font-size: 1.8em;
    color: #FFD43B;
    border-bottom: 2px solid #306998;
  }
  h2 {
    color: #306998;
  }
  code {
    font-size: 0.9em;
    background-color: #2D2D2D;
    color: #E0E0E0;
  }
  pre {
    background-color: #2D2D2D;
  }
  strong {
    color: #FFD43B;
  }
  a {
    color: #306998;
  }
  blockquote {
    border-left-color: #306998;
    color: #A0A0A0;
  }
  ul li::marker {
    color: #FFD43B;
  }
  ol li::marker {
    color: #FFD43B;
  }
  section.lead h1 {
    font-size: 2.5em;
  }
  section.lead h2 {
    font-size: 1.8em;
  }
  section.lead {
    text-align: center;
  }

---

# Layered Architecture & Dependency Injection
## The Perfect Recipe for Your FastAPI Project

Antonis Markoulis
Senior Staff Engineer @Orfium

28/05/2025

---

# Agenda

- Our Journey: From Django to FastAPI
- The Freedom of FastAPI
- High-Level Architecture Overview
- Layer 1: Presentation Layer
- What is Dependency Injection?
- Layer 2: Service Layer
- Layer 3: Persistence Layer
- DTOs: The Glue Between Layers
- Testing Strategy
- Trade-offs and Challenges
- What We Learned
- Q&A + Resources

---

# Our Journey: From Django to FastAPI

- Started with Django's fat models
- Testing was painful
- ORM queries were hard to maintain
- Performance issues with sync code
- FastAPI won us over with:
  - Async support
  - Modern Python features
  - Better performance
  - Cleaner architecture

---

# The Freedom of FastAPI

- Minimal framework, maximum flexibility
- No enforced architecture
- Freedom to experiment and evolve
- Perfect for organizational standards

Our journey to find the right architecture:
- Started with domain-driven design
- Experimented with Clean Architecture
- Tried classical MVC
- Found our sweet spot in Layered Architecture

Why Layered Architecture won:
- Simple enough for new team members
- Flexible enough for complex domains
- Consistent across all projects
- Perfect balance of structure and freedom

---

# High-Level Architecture Overview

```
┌─────────────────┐
│  Presentation   │
│  (FastAPI/CLI)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Business     │
│    (Services)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Persistence   │
│     (DAOs)      │
└─────────────────┘
```

- DTOs flow between layers
- Interfaces define contracts
- Implementations are injected
- Celery/CLI reuse same services

---

# Layer 1: Presentation Layer

```python
@router.post("/foos")
async def create_foo(
    foo: FooCreateDTO,
    foo_service: FooService = Depends(get_foo_service)
) -> FooResponseDTO:
    return await foo_service.create_foo(foo)
```

- Minimal logic
- DTO validation
- Service injection
- Same pattern for CLI/Celery

---

# What is Dependency Injection?

- Inversion of control
- Services don't create their dependencies
- Dependencies are provided from outside
- Enables testing and flexibility

```python
class DependencyService:
    def __init__(self, config: Config):
        self.config = config

    def get_foo_service(self) -> FooService:
        if self.config.is_feature_enabled():
            return EnhancedFooService()
        return StandardFooService()
```

---

# Layer 2: Service Layer (Business)

- Interface vs implementation
- Transaction management
- Business logic
- Testable with fake DAOs

```python
from abc import ABC, abstractmethod

class FooService(ABC):
    @abstractmethod
    async def create_foo(self, foo: FooCreateDTO) -> FooResponseDTO:
        ...

class StandardFooService(FooService):
    def __init__(self, foo_dao: FooDAO, uow: UnitOfWork):
        self.foo_dao = foo_dao
        self.uow = uow
```

---

# Layer 3: Persistence Layer (DAOs)

- Interface for each DAO
- Real implementation
- No direct DB calls in services
- Easy to swap implementations

```python
from abc import ABC, abstractmethod

class FooDAO(ABC):
    @abstractmethod
    async def create(self, foo: FooDTO) -> FooDTO:
        ...

class SQLAlchemyFooDAO(FooDAO):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, foo: FooDTO) -> FooDTO:
        db_foo = Foo(**foo.model_dump())
        self.session.add(db_foo)
        await self.session.commit()
        return FooDTO.model_validate(db_foo)
```

---

# DTOs: The Glue Between Layers

- Lightweight
- Validation-free
- Serialization-safe
- Flow between layers

```python
from pydantic import BaseModel
from decimal import Decimal
from typing import List

class FooItemDTO(BaseModel):
    name: str
    quantity: int

class FooDTO(BaseModel):
    id: str
    name: str
    items: List[FooItemDTO]
    total: Decimal
```

---

# Testing Strategy

```
┌─────────────────┐
│  Unit Tests     │
│  (Services)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Integration     │
│ Tests (DAOs)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  System Tests   │
│  (Endpoints)    │
└─────────────────┘
```

## Unit Tests (Services)
```python
async def test_create_foo():
    # Arrange
    mock_dao = MockFooDAO()
    service = FooService(mock_dao, MockUnitOfWork())

    # Act
    result = await service.create_foo(foo_input)

    # Assert
    assert result.name == foo_input.name
    mock_dao.create.assert_called_once()
```

## Integration Tests (DAOs)
```python
async def test_foo_dao_create():
    # Arrange
    async with AsyncSession(engine) as session:
        dao = SQLAlchemyFooDAO(session)

        # Act
        result = await dao.create(foo_dto)

        # Assert
        assert result.id is not None
        assert result.name == foo_dto.name
```

## System Tests (Endpoints)
```python
def test_create_foo_endpoint():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.post("/foos", json=foo_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == foo_data["name"]
```

- Unit: Mock dependencies, test business logic
- Integration: Test DAOs with real database
- System: End-to-end with TestClient

---

# Trade-offs and Challenges

- Boilerplate code
- Onboarding cost
- Sometimes overkill for tiny apps
- Initial setup complexity

But the benefits outweigh the costs:
- Maintainable code
- Testable code
- Flexible code
- Consistent patterns

---

# What We Learned + When to Use This

Works well for:
- Single-domain apps <50k LOC
- Teams who want long-term maintainability
- Complex business logic
- Multiple entrypoints

When not to use:
- Tiny projects
- Simple CRUD apps
- Prototypes

---

# Q&A + Resources

- GitHub repo: [link]
- Documentation: [link]
- Example code: [link]
- Contact: [email]

Thank you for your attention!
