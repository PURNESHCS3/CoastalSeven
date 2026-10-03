import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Product,
    Order,
    OrderItem
)
from app.schemas import OrderCreate
from app.dependencies import get_admin_user, get_current_user
from app.redis_client import redis_client
from app.websocket_manager import manager


router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)


@router.post("/")
async def create_order(
    order_data: OrderCreate,
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
        delivery_address=order_data.delivery_address.strip(),
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
    redis_client.delete("products:all")

    await manager.broadcast({
        "order_id": order.id,
        "user_id": current_user.id,
        "status": "confirmed"
    })

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "total_amount": total_amount,
        "delivery_address": order.delivery_address,
        "status": order.status
    }


@router.get("/")
def get_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role == "admin":
        return db.query(Order).all()

    return db.query(Order).filter(
        Order.user_id == current_user.id
    ).all()


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    query = db.query(Order).filter(Order.id == order_id)

    if current_user.role != "admin":
        query = query.filter(Order.user_id == current_user.id)

    order = query.first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user)
):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Order is already cancelled"
        )

    if order.status != "confirmed":
        raise HTTPException(
            status_code=409,
            detail=f"Cannot cancel an order with status '{order.status}'"
        )

    for item in order.items:
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product:
            product.stock += item.quantity

    order.status = "cancelled"
    db.commit()
    db.refresh(order)

    redis_client.delete("products:all")

    await manager.broadcast({
        "order_id": order.id,
        "user_id": order.user_id,
        "status": order.status
    })

    return {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "status": order.status
    }