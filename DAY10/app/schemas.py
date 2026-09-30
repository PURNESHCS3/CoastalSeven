from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


class UserLogin(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# JWT TOKEN SCHEMAS
# ============================================================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Keep TokenResponse as an alias-compatible schema
# for any other router/code that uses this name.

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ============================================================
# PRODUCT SCHEMAS
# ============================================================

class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    price: float = Field(
        ...,
        gt=0
    )

    stock: int = Field(
        ...,
        ge=0
    )

    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# CART SCHEMAS
# ============================================================

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(
        ...,
        gt=0
    )


class CartResponse(BaseModel):
    items: list[CartItem]


# ============================================================
# ORDER SCHEMAS
# ============================================================

class OrderItemCreate(BaseModel):
    product_id: int

    quantity: int = Field(
        ...,
        gt=0
    )


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )