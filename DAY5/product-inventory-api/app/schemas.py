from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if self.name is None and self.email is None:
            raise ValueError(
                "At least one field must be provided"
            )

        return self


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================
# PRODUCT SCHEMAS
# =========================

class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    price: float = Field(
        ...,
        gt=0
    )

    owner_id: int = Field(
        ...,
        gt=0
    )


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    price: float | None = Field(
        default=None,
        gt=0
    )

    @model_validator(mode="after")
    def validate_update(self):
        if (
            self.name is None
            and self.description is None
            and self.price is None
        ):
            raise ValueError(
                "At least one field must be provided"
            )

        return self


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    owner_id: int

    model_config = ConfigDict(
        from_attributes=True
    )