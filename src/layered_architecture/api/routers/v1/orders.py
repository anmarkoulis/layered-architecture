from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from layered_architecture.db.depends import get_db
from layered_architecture.dto.order import (
    OrderDTO,
    OrderInputDTO,
    OrderUpdateDTO,
)
from layered_architecture.dto.user import UserReadDTO
from layered_architecture.services.concrete.fake_auth import FakeAuthService
from layered_architecture.services.dependency import DependencyService

router = APIRouter()


@router.post("/", response_model=OrderDTO, status_code=201)
async def create_order(
    order_input: OrderInputDTO,
    db: AsyncSession = Depends(get_db),
    current_user: UserReadDTO = Depends(FakeAuthService.get_current_user),
) -> OrderDTO:
    """Create a new order.

    :param order_input: The order input data including service_type
    :type order_input: OrderInputDTO
    :param db: The database session to use
    :type db: AsyncSession
    :param current_user: The current authenticated user
    :type current_user: UserReadDTO
    :return: The created order
    :rtype: OrderDTO
    """
    order_service = await DependencyService.get_order_service(
        order_input.service_type,
        db,
    )
    return await order_service.create_order(order_input, current_user)


@router.get("/{order_id}/", response_model=OrderDTO)
async def check_order_status(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserReadDTO = Depends(FakeAuthService.get_current_user),
) -> OrderDTO:
    """Check the status of an order.

    :param order_id: The ID of the order to check
    :type order_id: str
    :param db: The database session to use
    :type db: AsyncSession
    :param current_user: The current authenticated user
    :type current_user: UserReadDTO
    :return: The order with its current status
    :rtype: OrderDTO
    :raises ValueError: If the order is not found
    """
    order_service = await DependencyService.get_order_service_by_id(
        order_id, db
    )
    return await order_service.check_status(order_id, current_user)


@router.patch("/{order_id}/", response_model=OrderDTO)
async def update_order(
    order_id: str,
    update_data: OrderUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: UserReadDTO = Depends(FakeAuthService.get_current_user),
) -> OrderDTO:
    """Update an existing order.

    :param order_id: The ID of the order to update
    :type order_id: str
    :param update_data: The data to update the order with
    :type update_data: OrderUpdateDTO
    :param db: The database session to use
    :type db: AsyncSession
    :param current_user: The current authenticated user
    :type current_user: UserReadDTO
    :return: The updated order
    :rtype: OrderDTO
    :raises ValueError: If the order is not found
    """
    order_service = await DependencyService.get_order_service_by_id(
        order_id, db
    )
    return await order_service.update_order(
        order_id, update_data, current_user
    )


@router.delete("/{order_id}/", response_model=OrderDTO)
async def cancel_order(
    order_id: str,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserReadDTO = Depends(FakeAuthService.get_current_user),
) -> OrderDTO:
    """Cancel an existing order.

    :param order_id: The ID of the order to cancel
    :type order_id: str
    :param reason: Optional reason for cancellation
    :type reason: str | None
    :param db: The database session to use
    :type db: AsyncSession
    :param current_user: The current authenticated user
    :type current_user: UserReadDTO
    :return: The cancelled order
    :rtype: OrderDTO
    :raises ValueError: If the order is not found
    """
    order_service = await DependencyService.get_order_service_by_id(
        order_id, db
    )
    return await order_service.cancel_order(order_id, current_user, reason)
