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
## A Recipe for Clean and Testable FastAPI Code

![Meetup Logo](https://secure.meetupstatic.com/photos/event/6/b/9/2/clean_443067538.webp)

Antonis Markoulis
Senior Staff Engineer @Orfium

28/05/2025

---

# Agenda

1. From Django to FastAPI

2. Layered Architecture

3. Dependency Inversion & Injection

4. Testing Strategy

5. Live Demo

6. Aftermath

---

# Our Journey: From Django ...

## The Legacy & Issues
- Legacy Django projects with suboptimal structure
- Fat models at best, spaghetti code at worst
- Performance issues from sync code and ORM queries
- Hard to implement new features
- Limited async capabilities

## Our Approach
- Kept existing Django services
- Only rewrote one critical project to FastAPI
- All new services built with FastAPI

---

# Our Journey: ... To FastAPI

## Why FastAPI Won
- **Performance**: Async-first, built for speed
- **Modern**: Latest Python features
- **Agility**: Freedom to structure our way
- **Developer Experience**: Better tooling and type hints
- No enforced architecture
- Perfect for organizational standards

## Our Architecture Evolution
- Started with domain-driven design
- Experimented with Clean Architecture
- Found our sweet spot in Layered Architecture

---

# High-Level Architecture Overview

<div style="display: flex; justify-content: center; align-items: center; height: 70vh;">
<img src="diagrams/generated/high_level_architecture.png" style="max-width: 80%;" />
</div>

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

Example Flow:
```
POST Request → Validated DTO → Service → DAO → DB → Response DTO
```

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

# Dependency Inversion Principle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     │     ┌─────────────┐     ┌─────────────┐
│ Component 1 │────▶│ Component 2 │────▶│ Component 3 │     │     │ Component 1 │────▶│ Interface 1 │
└─────────────┘     └─────────────┘     └─────────────┘     │     └─────────────┘     └──────┬──────┘
                                                            │                                │
                                                            │                                ▼
                                                            │                         ┌─────────────┐     ┌─────────────┐
                                                            │                         │ Component 2 │────▶│ Interface 2 │
                                                            │                         └─────────────┘     └──────┬──────┘
                                                            │                                                    │
                                                            │                                                    ▼
                                                            │                                             ┌─────────────┐
                                                            │                                             │ Component 3 │
                                                            │                                             └─────────────┘
```

- High-level modules should not depend on low-level modules
- Both should depend on abstractions
- Abstractions should not depend on details
- Details should depend on abstractions

---

# Dependency Injection with Dependency Service

```python
class DependencyService:
    @staticmethod
    def get_foo_service(
        db: AsyncSession = Depends(get_db),
    ) -> FooServiceInterface:
        uow = SQLAUnitOfWork(db)
        return FooService(
            foo_dao=FooDAO(uow.db),
            foo_client=FooClient(),
            uow=uow,
        )
```

- Simple service assembly
- Clear dependencies
- Easy to test
- Extensible (singletons, caching, feature flags)

---

# Testing Strategy

```
        ┌─────────────────┐
        │  System Tests   │
        │  (API/Celery)   │
        └────────┬────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │     Integration         │
    │     Tests (DAOs)        │
    └────────────┬────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│           Unit Tests            │
│           (Services)            │
└─────────────────────────────────┘
```

- System: End-to-end with all entry points
- Integration: Test DAOs with real database
- Unit: Mock all dependencies, test business logic

---

# System Tests

```python
class TestFooAPI:
    @pytest.mark.anyio
    async def test_get_foo(
        self,
        async_client: AsyncClient,  # async client of FastAPI
    ) -> None:
        # given
        payload = { bar: "bar" }
        response = await async_client.post("v1/foo/", json=payload)
        foo_id = response.json()["id"]

        # when
        response = await async_client.get(f"v1/foo/{foo_id}")

        # then
        assert response.status_code == 200
        assert response.json() == {
            "id": str(job.id),
            "bar": "bar",
        }
```

---

# Integration Tests

```python
class TestFooDAO:
    @pytest.mark.anyio
    async def test_create(
        self,
        test_session: AsyncSession,
    ) -> None:
        # Given
        dao = SQLAlchemyFooDAO(test_session)
        foo_dto = FooDTO(bar="bar")

        # When
        result = await dao.create(foo_dto)

        # Then
        assert result.bar == "bar"
```

---

# Unit Tests

```python
@pytest.mark.anyio
class TestFooService:
    async def test_foo_happy(self) -> None:
      # given
      foo_dao = AsyncMock(spec=FooDAOInterface)
      foo_client = AsyncMock(spec=FooClientInterface)
      foo_service = FooService(
        foo_dao=foo_dao,
        foo_client=foo_client
      )
      foo_id = "foo_id"
      foo_dao.get_one.return_value = FooDTO(bar="bar", id="foo_id")
      foo_client.get.return_value = FooDTO(bar="bar", id="foo_id")

      # when
      response = await foo_service.get_one(foo_id=foo_id)

      # then
      assert response == FooDTO(bar="bar", id="foo_id")
      foo_dao.get_one.assert_called_once_with(foo_id)
      foo_client.get.assert_called_once_with(foo_id)
```

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
