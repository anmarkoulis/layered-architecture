import logging
from typing import Optional, Tuple, Union

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.applications import Starlette
from starlette.responses import Response

from layered_architecture.dto import ErrorEnvelope, ErrorResponse
from layered_architecture.exceptions import (
    LayeredArchitectureException,
    NotFoundError,
)

logger = logging.getLogger(__name__)


def generate_response(
    status_code: int, errors: list[ErrorResponse]
) -> JSONResponse:
    """Generate a JSON response for the error."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorEnvelope(errors=errors).model_dump(exclude_none=True),
    )


class ErrorHandler:
    @staticmethod
    def extract_from_exception(
        exc: Union[ValidationError, RequestValidationError],
    ) -> Tuple[Optional[str], Optional[str], str]:
        """Extract key, message and details from validation error."""
        e = exc.errors()[0]
        key = str(e["loc"][-1]) if len(e["loc"]) > 1 else None
        return key, None, e["msg"]

    @classmethod
    async def not_found_error_handler(
        cls,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle not found errors."""
        if not isinstance(exc, NotFoundError):
            raise exc
        logger.warning(f"NotFoundError: {str(exc)}")
        return generate_response(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=[
                ErrorResponse(
                    code=exc.code,
                    details=exc.details,
                    message=exc.message,
                    key=exc.key,
                )
            ],
        )

    @classmethod
    async def layered_architecture_error_handler(
        cls,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle layered architecture exceptions."""
        if not isinstance(exc, LayeredArchitectureException):
            raise exc
        logger.error(f"{exc.__class__.__name__}: {str(exc)}")
        return generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=[
                ErrorResponse(
                    code=exc.code,
                    details=exc.details,
                    message=exc.message,
                    key=exc.key,
                )
            ],
        )

    @classmethod
    async def validation_error_handler(
        cls,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle validation errors."""
        if not isinstance(exc, (ValidationError, RequestValidationError)):
            raise exc
        logger.warning(f"ValidationError: {exc.errors()}")
        key, msg, details = cls.extract_from_exception(exc)
        return generate_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            errors=[
                ErrorResponse(
                    code="validation_error",
                    details=details,
                    message=msg,
                    key=key,
                )
            ],
        )

    @classmethod
    async def value_error_handler(
        cls,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle value errors."""
        if not isinstance(exc, ValueError):
            raise exc
        logger.warning(f"ValueError: {str(exc)}")
        return generate_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=[
                ErrorResponse(
                    code="invalid_value",
                    details=str(exc),
                )
            ],
        )

    @classmethod
    async def type_error_handler(
        cls,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle type errors."""
        if not isinstance(exc, TypeError):
            raise exc
        logger.warning(f"TypeError: {str(exc)}")
        return generate_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=[
                ErrorResponse(
                    code="invalid_type",
                    details=str(exc),
                )
            ],
        )

    @classmethod
    async def server_error_handler(
        cls, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle server errors."""
        logger.error(f"Server error: {exc}")
        error_msg = "An unexpected error occurred"
        return generate_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=[
                ErrorResponse(
                    code="server_error",
                    details=error_msg,
                )
            ],
        )


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure the global exception handlers for the application."""
    # Most specific handlers first
    app.add_exception_handler(
        RequestValidationError,
        ErrorHandler.validation_error_handler,
    )
    app.add_exception_handler(
        ValidationError,
        ErrorHandler.validation_error_handler,
    )
    app.add_exception_handler(
        NotFoundError,
        ErrorHandler.not_found_error_handler,
    )
    app.add_exception_handler(
        ValueError,
        ErrorHandler.value_error_handler,
    )
    app.add_exception_handler(
        TypeError,
        ErrorHandler.type_error_handler,
    )
    app.add_exception_handler(
        LayeredArchitectureException,
        ErrorHandler.layered_architecture_error_handler,
    )
    # Most general handler last
    app.add_exception_handler(
        Exception,
        ErrorHandler.server_error_handler,
    )


async def validation_exception_handler(
    request: Request, exc: Exception
) -> Response:
    if not isinstance(exc, (ValidationError, RequestValidationError)):
        raise exc
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


def register_error_handlers(app: Starlette) -> None:
    """Register error handlers for the Starlette application."""
    app.add_exception_handler(
        ValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        NotFoundError,
        ErrorHandler.not_found_error_handler,
    )
    app.add_exception_handler(
        ValueError,
        ErrorHandler.value_error_handler,
    )
    app.add_exception_handler(
        TypeError,
        ErrorHandler.type_error_handler,
    )
    app.add_exception_handler(
        LayeredArchitectureException,
        ErrorHandler.layered_architecture_error_handler,
    )
    app.add_exception_handler(
        Exception,
        ErrorHandler.server_error_handler,
    )
