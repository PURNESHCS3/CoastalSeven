import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Product,
    Order,
    OrderItem
)
from app.dependencies import get_current_user
from app.redis_client import redis_client
from app.tasks.email_tasks import (
    send_order_confirmation_email
)
from app.websocket_manager import manager


router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)


@router.post("/")
async def create_order(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    key = f"cart:{current_user.id}"

    cart = redis_client.get(key)

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    cart_data = json.loads(cart)

    total_amount = 0

    order_items = []

    for product_id, quantity in cart_data.items():

        product = db.query(Product).filter(
            Product.id == int(product_id),
            Product.is_active == True
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )

        if quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )

        total_amount += (
            product.price * quantity
        )

        order_items.append(
            {
                "product": product,
                "quantity": quantity
            }
        )

    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="confirmed"
    )

    db.add(order)
    db.flush()

    for item in order_items:

        product = item["product"]
        quantity = item["quantity"]

        product.stock -= quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price
        )

        db.add(order_item)

    db.commit()
    db.refresh(order)

    redis_client.delete(key)

    send_order_confirmation_email.delay(
        current_user.email,
        order.id,
        total_amount
    )

    await manager.broadcast({
        "order_id": order.id,
        "user_id": current_user.id,
        "status": "confirmed"
    })

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "total_amount": total_amount,
        "status": order.status
    }


@router.get("/")
def get_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order