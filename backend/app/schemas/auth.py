from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.therapist import TherapistResponse


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    therapist: TherapistResponse


class ResetPassword(BaseModel):
    new_password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters",
    )
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("new_password")
    @classmethod
    def validate_password_byte_length(cls, v: str) -> str:
        password_bytes = v.encode("utf-8")
        if len(password_bytes) > 72:
            raise ValueError(
                f"Password is too long ({len(password_bytes)} bytes). "
                "Maximum is 72 bytes (may be fewer characters if using special characters)."
            )
        return v
