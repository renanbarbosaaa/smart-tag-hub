from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class LinkCreate(BaseModel):
    target_url: str
    slug: str | None = None


class LinkUpdate(BaseModel):
    target_url: str | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "LinkUpdate":
        if self.target_url is None and self.is_active is None:
            raise ValueError("Informe target_url ou is_active.")
        return self


class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    target_url: str
    created_at: datetime
    is_active: bool
