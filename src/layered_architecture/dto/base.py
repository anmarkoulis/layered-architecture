from enum import Enum

from pydantic import BaseModel, ConfigDict


class ModelConfigBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, json_encoders={Enum: lambda x: x.value}
    )
