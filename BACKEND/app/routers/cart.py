import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import CartItem
from app.redis_client import redis_client
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api/cart",
    tags=["Cart"]
)


def cart_key(user_id: int):
    return f"cart:{user_id}"


@router.post("/add")
def add_to_cart(
    item: CartItem,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    key = cart_key(current_user.id)

    cart = redis_client.get(key)

    if cart:
        cart_data = json.loads(cart)
    else:
        cart_data = {}

    product_key = str(item.product_id)
    new_quantity = cart_data.get(product_key, 0) + item.quantity

    if new_quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    cart_data[product_key] = new_quantity

    redis_client.set(
        key,
        json.dumps(cart_data),
        ex=3600
    )

    return {
        "message": "Product added to cart",
        "cart": cart_data
    }


@router.get("/")
def get_cart(
    current_user=Depends(get_current_user)
):

    key = cart_key(current_user.id)

    cart = redis_client.get(key)

    if not cart:
        return {
            "cart": {}
        }

    return {
        "cart": json.loads(cart)
    }


@router.delete("/{product_id}")
def remove_from_cart(
    product_id: int,
    current_user=Depends(get_current_user)
):

    key = cart_key(current_user.id)

    cart = redis_client.get(key)

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart is empty"
        )

    cart_data = json.loads(cart)

    if str(product_id) not in cart_data:
        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    del cart_data[str(product_id)]

    redis_client.set(
        key,
        json.dumps(cart_data),
        ex=3600
    )

    return {
        "message": "Product removed from cart",
        "cart": cart_data
    }