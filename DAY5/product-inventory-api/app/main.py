from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)


app = FastAPI(
    title="Product Inventory API",
    description="A FastAPI CRUD application for users and products",
    version="1.0.0"
)


# =========================
# ROOT
# =========================

@app.get("/")
async def root():
    return {
        "message": "Product Inventory API is running!"
    }


# =========================
# USER ENDPOINTS
# =========================

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_user(db, user)


@app.get(
    "/users",
    response_model=list[UserResponse]
)
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_users(db)


@app.get(
    "/users/{user_id}",
    response_model=UserResponse
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@app.put(
    "/users/{user_id}",
    response_model=UserResponse
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return await crud.update_user(
        db,
        user,
        user_data
    )


@app.delete(
    "/users/{user_id}"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    await crud.delete_user(db, user)

    return {
        "message": "User deleted successfully"
    }


# =========================
# PRODUCT ENDPOINTS
# =========================

@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=201
)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check whether owner exists
    user = await crud.get_user(
        db,
        product.owner_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Owner user not found"
        )

    return await crud.create_product(
        db,
        product
    )


@app.get(
    "/products",
    response_model=list[ProductResponse]
)
async def get_products(
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_products(db)


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product = await crud.get_product(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    product = await crud.get_product(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return await crud.update_product(
        db,
        product,
        product_data
    )


@app.delete(
    "/products/{product_id}"
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product = await crud.get_product(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    await crud.delete_product(
        db,
        product
    )

    return {
        "message": "Product deleted successfully"
    }