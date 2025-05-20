# Python Meetup Presentation

## Title
"Layered Architecture & Dependency Injection: A Recipe for Clean and Testable FastAPI Code"

## Architectural Evolution

### The Legacy & Issues
- Legacy Django projects with suboptimal structure
- Fat models at best, spaghetti code at worst
- Performance issues from sync code and ORM queries
- Difficult to maintain, scale, and test

### Why FastAPI Won
- **Performance**: Async-first, built for speed
- **Modern**: Latest Python features
- **Agility**: Freedom to structure our way

### Our Architecture Evolution
- Started with domain-driven design
- Experimented with Clean Architecture
- Found our sweet spot in Layered Architecture

### Why Layered Architecture?
- Simple enough for new team members
- Flexible enough for complex domains
- Consistent across all projects
- Perfect balance of structure and freedom
- Easy to understand and maintain
- Scales well with team size
- Works for both simple and complex projects

## Description options


1. Ever wondered how to build scalable, testable, and maintainable services with FastAPI?
In this talk, we'll walk through the full lifecycle of a request in our production-ready FastAPI setup—from the entry point all the way to the database and back. We'll show how we use layered architecture with strict boundaries between presentation, business, and persistence layers, leveraging dependency injection to keep everything decoupled and testable.
We'll also share why we moved away from Django's fat models and ORM magic, how this new design improved our flexibility and testability, and what trade-offs (like boilerplate!) we had to accept.
Whether you're scaling a side project or architecting microservices, this talk will help you structure your Python codebase like a pro.

2. Tired of untestable code and tight coupling in your FastAPI applications? We've been there too. In this practical talk, we'll share our journey of transforming a monolithic Django application into a maintainable FastAPI service. You'll see how layered architecture and dependency injection helped us break free from the limitations of fat models and magic ORM queries. We'll discuss real challenges we faced, the trade-offs we made, and how this architecture made our code more testable and flexible. Whether you're dealing with legacy code or starting fresh, you'll leave with actionable patterns you can apply immediately.

3. Building a FastAPI application that scales? It's not just about async endpoints and Pydantic models. In this talk, we'll dive deep into how we structure our FastAPI applications for long-term maintainability. You'll learn how we use layered architecture to keep our code organized, how dependency injection helps us write testable code, and why we moved away from the traditional Django approach. We'll share real examples of how this architecture helped us handle complex business logic, scale our services, and maintain high test coverage. Plus, we'll discuss the trade-offs and when this approach might be overkill.

4. FastAPI is great, but how do you structure a real-world application that grows with your business? In this talk, we'll share our experience building production-grade FastAPI services using layered architecture. You'll see how we handle complex business logic, maintain testability, and scale our applications. We'll discuss why we moved away from Django's approach, how we manage dependencies, and what trade-offs we made along the way. Whether you're building a new service or refactoring an existing one, you'll learn practical patterns you can apply to your own projects.

5. Want to build FastAPI applications that don't turn into spaghetti code? In this talk, we'll show you how we use layered architecture to keep our code organized and maintainable. You'll learn how we structure our applications, handle dependencies, and write testable code. We'll share real examples of how this approach helped us scale our services and maintain high test coverage. Plus, we'll discuss the trade-offs and when this architecture might be overkill. Whether you're new to FastAPI or a seasoned developer, you'll leave with practical patterns you can apply to your own projects.

## Presentation Slides


Suggested Slide Flow (for 20–30 mins):
	1.	[Title Slide]
	•	Include title, your name, company (optional), and agenda.
	2.	[Our Journey: From Django to FastAPI]
	•	Brief story: fat models, testing pain, ORM queries, performance.
	•	Show a rough timeline and why FastAPI won.
	3.	[High-Level Architecture Overview]
	•	One diagram with layers: Presentation → Business → Persistence.
	•	Label the DTOs, interfaces, and implementations.
	•	Mention Celery/CLI reuse.
	4.	[Layer 1: Presentation Layer]
	•	Show a FastAPI endpoint with Depends, service injection, DTO input.
	•	Mention how this also applies to CLI/Celery.
	•	Emphasize minimal logic here.
	5.	[What is Dependency Injection?]
	•	Explain inversion of control briefly.
	•	Show what the DependencyService does (simple code).
	•	How it injects services/DAOs based on config/env.
	6.	[Layer 2: Service Layer (Business)]
	•	Interface vs implementation: why and how.
	•	How transaction management and logic live here.
	•	Emphasize testability with fake daos.
	7.	[Layer 3: Persistence Layer (DAOs)]
	•	Interface for each DAO + real implementation.
	•	Explain why you avoid direct DB calls in services.
	8.	[DTOs: The Glue Between Layers]
	•	Lightweight, validation-free, serialization-safe.
	9.	[Testing Strategy]
	•	Diagram or example: service tested with fake/null daos.
	•	Benefits: fast, isolated, independent of DB.
	10.	[Trade-offs and Challenges]

	•	Boilerplate.
	•	Onboarding cost.
	•	Sometimes overkill for tiny apps.

	11.	[What We Learned + When to Use This]

	•	Works well for single-domain apps <50k LOC.
	•	Great for teams who want long-term maintainability.
	•	When not to over-engineer.

	12.	[Q&A + Resources]

	•	Offer a GitHub repo/sample if available.
	•	Invite feedback/discussion.

## Developer Perspectives

### Junior Developer
"I appreciate the clear structure and separation of concerns. It makes it easier to understand where to put new code. The DTO pattern helps me validate data correctly."

### Mid-Level Developer
"The dependency injection pattern is powerful. I can easily swap implementations for testing. The layered architecture makes the codebase more maintainable."

### Senior Developer
"I see the value in avoiding if-statements through specialized implementations. The consistency across different entrypoints (API, CLI, Celery) is impressive."

### Staff Engineer
"The architecture scales well. We can easily add new features without modifying existing code. The testing strategy is comprehensive and maintainable."

#### General

1. "DependencyService" Sounds Vague
	•	Question: What is the DependencyService really doing? Is it a homegrown service container? How is it configured?
	•	Suggestion: Add a visual and small code snippet showing how DependencyService works, what its interface looks like, and how it decides which implementation to provide.

2. Interfaces Everywhere: Why So Many?
	•	Question: Why do you need an interface for each service and DAO if you only have one implementation? Isn't that overengineering?
	•	Suggestion: Clarify that interfaces aren't for current complexity, but to enable future flexibility and testability. Mention mock/fake/alternate implementations during testing or per environment.

3. Unit of Work: Explain It
	•	Question: What is a "unit of work"? Is it a library? Is it your own pattern? How does it manage transactions?
	•	Suggestion: Include a slide or code snippet showing how your UnitOfWork class is used in a service, how it commits/rolls back, and why it's essential.

4. "DTOs" vs "Pydantic Schemas"
	•	Question: Why not just use Pydantic models all the way through? What's the difference between your DTOs and the FastAPI models?
	•	Suggestion: Clarify your DTOs are plain dataclasses (or Pydantic BaseModels with custom config?) and you intentionally decouple them from request/response schemas.

5. Boilerplate: Can It Be Minimized?
	•	Question: Is there a code generation approach or shared pattern to reduce the boilerplate?
	•	Suggestion: Acknowledge boilerplate is a trade-off and share any ideas you're exploring to reduce it (e.g., abstract base classes, codegen, or common service mixins).


## Q&A Section

### Dependency Injection
Q: Why not use FastAPI's built-in dependency injection?
A: While FastAPI's DI is great, our custom DependencyService provides more control over implementation selection and lifecycle management.

Q: How do you handle circular dependencies?
A: We use interface segregation and careful service design to avoid circular dependencies. Sometimes we introduce a mediator service.

### Async Services
Q: Why async services instead of sync?
A: Async services allow better resource utilization and scalability, especially when dealing with I/O operations.

Q: How do you handle async context managers?
A: We use async context managers in our services and ensure proper cleanup in the unit of work pattern.

### Testing Strategy
Q: How do you test async services?
A: We use pytest-asyncio and create async test fixtures. Our fake services implement the same interfaces.

Q: What's your approach to integration testing?
A: We use a test database and transaction rollbacks to ensure test isolation.

### Tradeoffs
Q: Isn't this architecture overkill for small projects?
A: The initial setup might seem like overkill, but it pays off as the project grows. We have templates to reduce boilerplate.

Q: How do you handle the learning curve for new team members?
A: We provide extensive documentation and pair programming sessions. The consistent patterns make it easier to learn.

### Comparison to Other Architectures
Q: How does this compare to Clean Architecture?
A: Our approach is inspired by Clean Architecture but simplified for practical use. We focus on the core principles that provide the most value.

Q: Why not use a framework like Django?
A: FastAPI's async support and modern Python features make it a better fit for our use cases.

### DTOs
Q: Why DTOs instead of Pydantic models?
A: We use Pydantic for our DTOs but call them DTOs to emphasize their role in data transfer.

Q: How do you handle DTO validation?
A: Validation happens at the boundaries (API endpoints, CLI commands) using Pydantic's validation features.

### Celery and CLI Integration
Q: How do you share code between FastAPI and Celery?
A: We use the same service interfaces and DTOs across all entrypoints.

Q: How do you handle CLI-specific concerns?
A: We use Typer for CLI and inject appropriate service implementations through our DependencyService.

### Codebase Growth
Q: How do you maintain consistency as the codebase grows?
A: We use strict linting rules, automated testing, and code reviews to maintain consistency.

Q: How do you handle feature flags and A/B testing?
A: We implement different service implementations and select them through our DependencyService based on feature flags.

## Tools for Creating Presentations

For converting this markdown to a presentation, you can use:

1. **Marp**: A markdown presentation ecosystem
   - Install: `npm install -g @marp-team/marp-cli`
   - Convert: `marp presentation.md --pdf`

2. **Slidev**: A slide maker and presenter
   - Install: `npm init slidev`
   - Convert: `slidev build`

3. **Reveal.js**: A framework for creating presentations
   - Install: `npm install reveal-md`
   - Convert: `reveal-md presentation.md --static _site`

4. **Pandoc**: A universal document converter
   - Install: `brew install pandoc`
   - Convert: `pandoc presentation.md -o presentation.pdf`

I recommend using Marp as it's specifically designed for markdown presentations and produces clean, professional-looking slides.

# Testing Strategy

## System Tests
- Test complete request flow
- Use FastAPI's AsyncClient
- Test API contracts
- Follow given/when/then pattern

### Guidelines
- No mocking whatsoever in e2e tests
- Use mock servers for external services
- Use test endpoints to create resources (not in production)
- Avoid factories (they could break with DAO refactoring)

Example:
```python
class TestFooAPI:
    @pytest.mark.anyio
    async def test_get_foo(
        self,
        async_client: AsyncClient,
    ) -> None:
        # given
        payload = { bar: "bar" }
        response = await async_client.post("v1/foo/", json=payload)
        foo_id = response.json()["id"]

        # when
        response = async_client.get(f"v1/foo/{foo_id}")

        # then
        assert response.status_code == 200
        assert response.json() == {
            "id": str(job.id),
            "bar": "bar",
        }
```

## Integration Tests
- Test DAOs against real database
- Validate SQL queries and constraints
- Test transaction boundaries
- Use test database with rollbacks
- Focus on data persistence
- Verify database state

Example:
```python
@pytest.mark.anyio
async def test_foo_dao_create(db: AsyncSession) -> None:
    # Arrange
    dao = SQLAlchemyFooDAO(db)
    foo_dto = FooDTO(name="test", items=[])

    # Act
    result = await dao.create(foo_dto)

    # Assert
    assert result.id is not None
    assert result.name == foo_dto.name

    # Verify in database
    db_foo = await db.get(Foo, result.id)
    assert db_foo is not None
    assert db_foo.name == foo_dto.name
```

## Unit Tests
- Mock all dependencies
- Focus on business logic
- Fast execution
- Test edge cases
- Verify business rules
- Use AsyncMock for async dependencies
- Test service behavior in isolation

Example:
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
        response = foo_service.get_one(foo_id=foo_id)

        # then
        assert response == FooDTO(bar="bar", id="foo_id")
        foo_dao.get_one.assert_called_once_with(foo_id)
        foo_client.get.assert_called_once_with(foo_id)
```

## Benefits
- Clear separation of concerns
- Fast feedback loop
- Easy to maintain
- Good coverage
- Realistic testing

## Trade-offs
- More test files
- Need to maintain test database
- System tests can be slow
- Need to handle async testing

# DTOs: The Glue Between Layers

## Why Pydantic Models?
- Built-in validation
- JSON serialization
- Type safety
- Easy to extend

## Example DTOs
```python
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List

class FooItemDTO(BaseModel):
    name: str = Field(..., description="The name of the item")
    quantity: int = Field(..., ge=1, description="The quantity of the item")

class FooDTO(BaseModel):
    id: str = Field(..., description="The unique identifier")
    name: str = Field(..., description="The name of the foo")
    items: List[FooItemDTO] = Field(..., description="The items in the foo")
    total: Decimal = Field(..., description="The total amount")
```

## Benefits
- Automatic validation
- Clear documentation
- Type hints
- Easy serialization
- Schema generation
