from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LinkCreate(BaseModel):
    target_url: str
    slug: str | None = None


class LinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    target_url: str
    created_at: datetime