from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class OrganizationUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    logo_url: str | None = Field(
        default=None,
        max_length=500,
    )
