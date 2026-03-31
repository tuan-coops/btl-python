from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RoleSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: RoleSchema

    model_config = ConfigDict(from_attributes=True)
