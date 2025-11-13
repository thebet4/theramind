from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator


class TherapistBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    professional_license: Optional[str] = None


class TherapistCreate(BaseModel):
    email: EmailStr
    full_name: str
    professional_license: str
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters",
    )
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, v: str) -> str:
        password_bytes = v.encode("utf-8")
        if len(password_bytes) > 72:
            raise ValueError(
                f"Password is too long ({len(password_bytes)} bytes). "
                "Maximum is 72 bytes (may be fewer characters if using special characters)."
            )
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class TherapistLogin(BaseModel):
    email: EmailStr
    password: str


class TherapistResponse(TherapistBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    therapist: TherapistResponse
