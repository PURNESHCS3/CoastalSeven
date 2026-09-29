from fastapi import FastAPI

from app.routers import (
    auth,
    products,
    cart,
    orders,
    websocket
)


app = FastAPI(
    title="E-Commerce API",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(websocket.router)