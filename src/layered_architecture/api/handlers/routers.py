from fastapi import FastAPI
from starlette.responses import RedirectResponse

from layered_architecture.api.routers.api_router import api_router
from layered_architecture.dto import HealthResponse


def configure_routers(app: FastAPI) -> None:
    """
    Configures the application's API routers.
    """
    app.include_router(api_router)

    @app.get(
        "/ht/",
        description="Health check endpoint to indicate service status",
        tags=["health"],
        response_model=HealthResponse,
        responses={
            200: {
                "description": "Service is healthy",
                "content": {"application/json": {"example": {"status": "UP"}}},
            }
        },
    )
    async def health_check() -> HealthResponse:
        """
        Health check endpoint to indicate service status.
        """
        return HealthResponse(status="UP")

    @app.get("/", include_in_schema=False)
    async def docs_redirect() -> RedirectResponse:
        """
        Redirects the root URL to the API docs.
        """
        return RedirectResponse(url="docs")
