# Python Meetup Presentation

## Title
"Layered Architecture & Dependency Injection: A Recipe for Clean and Testable FastAPI Code"

## Description
Building a FastAPI application that scales? It's not just about async endpoints and Pydantic models. In this talk, we'll dive deep into how we structure our FastAPI applications for long-term maintainability. You'll learn how we use layered architecture to keep our code organized, how dependency injection helps us write testable code, and why we moved away from the traditional Django approach. We'll share real examples of how this architecture helped us handle complex business logic, scale our services, and maintain high test coverage. Plus, we'll discuss the trade-offs and when this approach might be overkill.

## Presentation Flow (Total: 30 minutes)

1. From Django to FastAPI (5 minutes)

[Presenter Notes]
"Let me start by sharing our journey from Django to FastAPI. Many of us have worked with Django - it's a fantastic framework that has served the Python community well for years. However, as our needs evolved, we found ourselves facing some challenges.

Our legacy Django projects had what we call 'fat models' - where all the business logic lived in the models. At worst, we had spaghetti code that was hard to maintain and test. The synchronous nature of Django and its ORM queries were causing performance bottlenecks, especially as our user base grew.

We made a strategic decision: instead of rewriting everything at once, we kept our existing Django services and only rewrote one critical project to FastAPI. All new services would be built with FastAPI.

Why FastAPI? Three key reasons: First, it's async-first, built for speed. Second, it embraces modern Python features. And third, it gives us the freedom to structure our code our way, without enforcing a specific architecture.

Our architecture evolution started with domain-driven design, then we experimented with Clean Architecture, and finally found our sweet spot in Layered Architecture. This approach gives us the perfect balance of structure and flexibility."

2. Layered Architecture (7 minutes)

[Presenter Notes]
"Let me show you our layered architecture. [Show diagram] It consists of three main layers: Presentation, Business, and Persistence.

The Presentation Layer is where FastAPI lives. It's responsible for handling HTTP requests, validating input, and formatting responses. The same pattern works for CLI commands and Celery tasks.

Here's a simple example of how it looks in code: [Show code example]
```python
@router.post("/foos")
async def create_foo(
    foo: FooCreateDTO,
    foo_service: FooService = Depends(get_foo_service)
) -> FooResponseDTO:
    return await foo_service.create_foo(foo)
```

The Business Layer contains our services. This is where the magic happens - all our business logic lives here. Services are defined by interfaces, making them easy to test and swap implementations.

The Persistence Layer handles all database operations through DAOs - Data Access Objects. Each DAO has an interface, and we can easily swap implementations for different databases or testing.

This separation of concerns brings several benefits:
- Improves code organization and maintainability
- Simplifies testing through clear boundaries
- Enables independent scaling of each layer
- Makes it easier to swap implementations

DTOs - Data Transfer Objects - flow between these layers. They're lightweight, validation-free, and safe for serialization. They ensure our business logic isn't coupled to our database schema or API contracts.

The beauty of this architecture is its simplicity. New team members can understand it quickly, yet it's flexible enough to handle complex domains. It's consistent across all our projects, making it easy to maintain and scale."

3. Dependency Inversion & Injection (5 minutes)

[Presenter Notes]
"Now, let's talk about dependency inversion and injection. This is a crucial principle that makes our architecture work.

The Dependency Inversion Principle states that high-level modules should not depend on low-level modules. Both should depend on abstractions. In practice, this means our services don't know about specific database implementations or external services.

We implement this through our DependencyService. Here's how it works: [Show code example]
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

This approach gives us several benefits:
- We can easily swap implementations for testing
- Our code is more maintainable and testable
- We avoid circular dependencies
- It's simple to understand and use

The key is that our services depend on interfaces, not concrete implementations. This makes our code more flexible and easier to test."

4. Testing Strategy (5 minutes)

[Presenter Notes]
"Our testing strategy follows the testing pyramid approach. Let me show you how we test each layer.

System tests are at the top. These test the complete flow from API to database. We use FastAPI's AsyncClient and follow the given/when/then pattern. Here's an example: [Show code example]
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
        response = await async_client.get(f"v1/foo/{foo_id}")

        # then
        assert response.status_code == 200
        assert response.json() == {
            "id": str(job.id),
            "bar": "bar",
        }
```

Integration tests verify our DAOs work correctly with the real database. We use a test database with rollbacks to ensure test isolation. These tests validate our infrastructure wiring and database interactions.

Unit tests focus on business logic. We mock all dependencies and test services in isolation. This gives us fast feedback and good coverage. The key is that we're testing the business logic in isolation, not the infrastructure.

The key to our testing strategy is that we never mock in system tests. This ensures we're testing the real behavior of our application."

5. Live Demo (5 minutes)

[Presenter Notes]
"Let's see this in action with our pizza & beer ordering system. This is a real-world example that shows all layers working together.

[Start demo]
Here we have a complete flow:
- API endpoint for creating orders
- Service layer handling business logic
- Multiple external service integrations
- Transaction management
- Error handling
- Full test coverage

[Run through the demo, showing:
1. Creating an order
2. How the layers interact
3. Running the tests
4. Error handling]

This demonstrates how all the concepts we've discussed come together in a real application. Notice how clean and maintainable the code is, and how easy it is to test.

You can find the complete source code in our GitHub repository. [Show QR code]"

6. Tips for Getting Started (3 minutes)

[Presenter Notes]
"Before we wrap up, let me share some practical tips for adopting this architecture:

1. Define DTOs first – they drive the whole flow
2. Start with 1 service to test layering
3. Use interfaces from day 1 (even simple ones)
4. Keep dependency injection centralized
5. Add tests early (unit > integration > system)

These tips will help you get started on the right foot and avoid common pitfalls."

7. Closing (2 minutes)

[Presenter Notes]
"Thank you all for your attention! I hope you found this talk valuable. You can find all the code and examples in our GitHub repository. Feel free to connect with me on LinkedIn or Twitter to continue the conversation about clean code, pizza, and async Python! 🍕"

## Anticipated Questions

[Presenter Notes]
"Let me prepare you for some common questions you might get:

1. Why not use FastAPI's built-in dependency injection?
   - While FastAPI's DI is great, our custom DependencyService provides more control over implementation selection and lifecycle management.

2. How do you handle circular dependencies?
   - We use interface segregation and careful service design to avoid circular dependencies. Sometimes we introduce a mediator service.

3. How do you test async services?
   - We use pytest-asyncio and create async test fixtures. Our fake services implement the same interfaces.

4. Isn't this architecture overkill for small projects?
   - The initial setup might seem like overkill, but it pays off as the project grows. We have templates to reduce boilerplate.

5. How do you handle the learning curve for new team members?
   - We provide extensive documentation and pair programming sessions. The consistent patterns make it easier to learn."

## Resources
- GitHub repository: github.com/anmarkoulis/layered-architecture
- Documentation: [link]
- Example code: [link]
- Contact: antonis@orfium.com
- LinkedIn: linkedin.com/in/anmarkoulis
- Twitter: twitter.com/anmarkoulis
