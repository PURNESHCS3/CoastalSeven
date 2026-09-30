from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Product
from app.schemas import (
    UserCreate,
    UserUpdate,
    ProductCreate,
    ProductUpdate,
)


async def create_user(
    db: AsyncSession,
    user_data: UserCreate
):
    user = User(
        name=user_data.name,
        email=user_data.email
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def get_users(
    db: AsyncSession
):
    result = await db.execute(
        select(User)
    )

    return result.scalars().all()


async def get_user(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user: User,
    user_data: UserUpdate
):
    update_data = user_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


async def delete_user(
    db: AsyncSession,
    user: User
):
    await db.delete(user)

    await db.commit()



async def create_product(
    db: AsyncSession,
    product_data: ProductCreate
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        owner_id=product_data.owner_id
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product


async def get_products(
    db: AsyncSession
):
    result = await db.execute(
        select(Product)
    )

    return result.scalars().all()


async def get_product(
    db: AsyncSession,
    product_id: int
):
    result = await db.execute(
        select(Product).where(
            Product.id == product_id
        )
    )

    return result.scalar_one_or_none()


async def update_product(
    db: AsyncSession,
    product: Product,
    product_data: ProductUpdate
):
    update_data = product_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product


async def delete_product(
    db: AsyncSession,
    product: Product
):
    await db.delete(product)

    await db.commit()