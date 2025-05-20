from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.db.depends import get_db
from layered_architecture.dto.order import OrderDTO, OrderInputDTO
from layered_architecture.services.dependency import DependencyService

router = APIRouter(prefix="/orders")


@router.post("/", response_model=OrderDTO)
async def create_order(
    order_input: OrderInputDTO, db: AsyncSession = Depends(get_db)
) -> OrderDTO:
    """Create a new order.

    Args:
        order_input: The order input data including store_type

    Returns:
        The created order
    """
    order_service = DependencyService.get_order_service(
        order_input.store_type, db
    )
    return await order_service.create_order(order_input)
