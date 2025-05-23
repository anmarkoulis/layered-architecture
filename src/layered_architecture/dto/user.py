from typing import Annotated, Optional

from pydantic import Field

from .base import ModelConfigBaseModel


class UserReadDTO(ModelConfigBaseModel):
    """DTO for reading user data."""

    id: Annotated[str, Field(description="The unique identifier of the user")]
    username: Annotated[str, Field(description="The username of the user")]
    first_name: Annotated[str, Field(description="The first name of the user")]
    last_name: Annotated[str, Field(description="The last name of the user")]
    email: Annotated[str, Field(description="The email address of the user")]
    address: Optional[
        Annotated[str, Field(description="The address of the user")]
    ] = None
