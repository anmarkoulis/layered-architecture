from fastapi import FastAPI

from layered_architecture.api.handlers import (
    configure_exception_handlers,
    configure_middlewares,
    configure_routers,
)
from layered_architecture.config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    description=settings.DESCRIPTION,
    debug=settings.DEBUG,
    version=settings.VERSION,
    docs_url="/docs",
)

configure_exception_handlers(app)
configure_middlewares(app)
configure_routers(app)
