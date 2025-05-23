class LayeredArchitectureException(Exception):
    """Base exception for the layered architecture."""

    def __init__(
        self,
        code: str,
        details: str,
        message: str | None = None,
        key: str | None = None,
    ) -> None:
        """Initialize the exception.

        :param code: The error code
        :type code: str
        :param details: The error details
        :type details: str
        :param message: Optional error message
        :type message: str | None
        :param key: Optional key associated with the error
        :type key: str | None
        """
        self.code = code
        self.details = details
        self.message = message
        self.key = key
        super().__init__(details)


class NotFoundError(LayeredArchitectureException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: str | None = None,
        key: str | None = None,
    ) -> None:
        """Initialize the not found error.

        :param resource_type: The type of resource that was not found (e.g., 'order', 'pizza')
        :type resource_type: str
        :param resource_id: The ID of the resource that was not found
        :type resource_id: str
        :param message: Optional error message
        :type message: str | None
        :param key: Optional key associated with the error
        :type key: str | None
        """
        details = f"{resource_type.capitalize()} {resource_id} not found"
        super().__init__(
            code="not_found",
            details=details,
            message=message,
            key=key,
        )
