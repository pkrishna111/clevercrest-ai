from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    organization_name: str = Field(
        min_length=1,
        max_length=255,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.lower()

        if "@" not in value:
            raise ValueError("Invalid email address.")

        return value

    @field_validator("first_name", "organization_name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str | None) -> str | None:
        if value == "":
            return None

        return value


class RegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.lower()

        if "@" not in value:
            raise ValueError("Invalid email address.")

        return value


class LoginResponse(BaseModel):
    message: str

class VerifyEmailResponse(BaseModel):
    message: str

class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: str = Field(
        min_length=3,
        max_length=320,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.lower()

        if "@" not in value:
            raise ValueError("Invalid email address.")

        return value


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    token: str = Field(
        min_length=1,
        max_length=512,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class ResetPasswordResponse(BaseModel):
    message: str


class CurrentUserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str | None
    is_email_verified: bool
    status: str