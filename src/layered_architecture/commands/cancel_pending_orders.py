import asyncio
import logging
import logging.config
import sys
from typing import Optional

import typer

from layered_architecture.config.settings import settings
from layered_architecture.db.models.order import ServiceType
from layered_architecture.db.session import AsyncDBContextManager
from layered_architecture.services.dependency import DependencyService

# Configure logging
logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("layered_architecture")

app = typer.Typer(
    name="cancel-pending-orders",
    help="Cancel all pending orders",
    add_completion=False,
)


async def _cancel_pending_orders(
    reason: Optional[str],
) -> None:
    """Cancel all pending orders.

    :param reason: Optional reason for cancellation
    :type reason: Optional[str]
    """
    try:
        async with AsyncDBContextManager() as db:
            logger.info("Starting cancellation of pending orders")
            auth_service = await DependencyService.get_auth_service()
            system_user = await auth_service.get_system_user()
            service = await DependencyService.get_order_service(
                ServiceType.get_default(), db
            )

            cancelled_orders = await service.cancel_pending_orders(
                system_user, reason
            )

            if cancelled_orders:
                logger.info(
                    f"Cancelled {len(cancelled_orders)} pending orders"
                )
                typer.echo(
                    f"Cancelled {len(cancelled_orders)} pending orders:"
                )
                for order in cancelled_orders:
                    typer.echo(f"- Order {order.id}: {order.status}")
            else:
                logger.info("No pending orders found to cancel")
                typer.echo("No pending orders found to cancel.")
    except Exception as e:
        logger.error(f"Error cancelling orders: {str(e)}", exc_info=True)
        raise


@app.command()
def cancel_pending_orders(
    reason: Optional[str] = typer.Option(
        None,
        "--reason",
        "-r",
        help="Optional reason for cancellation",
    ),
) -> None:
    """Cancel all pending orders.

    This command will cancel all pending orders using the default service type (DINE_IN).
    """
    try:
        logger.info("Starting cancel_pending_orders command")
        asyncio.run(_cancel_pending_orders(reason))
        logger.info("Successfully completed cancel_pending_orders command")
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        typer.echo("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(
            f"Error in cancel_pending_orders command: {str(e)}", exc_info=True
        )
        typer.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
