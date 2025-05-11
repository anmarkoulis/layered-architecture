from fastapi import APIRouter

from .orders import router as order_router

router = APIRouter()

router.include_router(order_router, prefix="/orders", tags=["orders"])
