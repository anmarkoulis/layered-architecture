import pytest
from freezegun import freeze_time
from httpx import AsyncClient

from layered_architecture.dto.order import ServiceType

pytestmark = pytest.mark.asyncio


class TestOrdersAPI:
    """Test the orders API endpoints."""

    async def test_create_dine_in_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a dine-in order.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.DINE_IN,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Margherita",
                    "quantity": 2,
                    "price": 12.99,
                }
            ],
            "notes": "Extra cheese please",
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["service_type"] == ServiceType.DINE_IN
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "pizza"
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["price"] == "12.99"
        assert data["notes"] == "Extra cheese please"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_delivery_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a delivery order.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.DELIVERY,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Pepperoni",
                    "quantity": 1,
                    "price": 14.99,
                }
            ],
            "notes": "Ring the doorbell twice",
            "delivery_address": "123 Main St",
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["service_type"] == ServiceType.DELIVERY
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "pizza"
        assert data["items"][0]["quantity"] == 1
        assert data["items"][0]["price"] == "14.99"
        assert data["notes"] == "Ring the doorbell twice"
        assert data["delivery_address"] == "123 Main St"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_takeaway_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a takeaway order.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.TAKEAWAY,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Quattro Formaggi",
                    "quantity": 1,
                    "price": 16.99,
                },
                {
                    "type": "beer",
                    "product_name": "Heineken",
                    "quantity": 2,
                    "price": 5.99,
                },
            ],
            "notes": "Ready in 20 minutes",
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["service_type"] == ServiceType.TAKEAWAY
        assert data["status"] == "pending"
        assert len(data["items"]) == 2
        assert data["items"][0]["type"] == "pizza"
        assert data["items"][0]["quantity"] == 1
        assert data["items"][0]["price"] == "16.99"
        assert data["items"][1]["type"] == "beer"
        assert data["items"][1]["quantity"] == 2
        assert data["items"][1]["price"] == "5.99"
        assert data["notes"] == "Ready in 20 minutes"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @freeze_time("2024-03-19 23:00:00")  # 11 PM
    async def test_create_late_night_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a late night order.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.LATE_NIGHT,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Diavola",
                    "quantity": 1,
                    "price": 15.99,
                }
            ],
            "notes": "After hours delivery",
            "delivery_address": "456 Night St",
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["service_type"] == ServiceType.LATE_NIGHT
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "pizza"
        assert data["items"][0]["quantity"] == 1
        assert data["items"][0]["price"] == "15.99"
        assert data["notes"] == "After hours delivery"
        assert data["delivery_address"] == "456 Night St"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_dine_in_order_invalid_pizza(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a dine-in order with an invalid pizza."""
        order_data = {
            "service_type": "dine_in",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "invalid_pizza",
                    "quantity": 1,
                }
            ],
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Pizza invalid_pizza not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_create_dine_in_order_invalid_beer(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a dine-in order with an invalid beer."""
        order_data = {
            "service_type": "dine_in",
            "items": [
                {
                    "type": "beer",
                    "product_name": "invalid_beer",
                    "quantity": 1,
                }
            ],
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Beer invalid_beer not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_create_dine_in_order_zero_quantity(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a dine-in order with zero quantity.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.DINE_IN,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Margherita",
                    "quantity": 0,
                }
            ],
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 422
        assert "quantity" in response.text.lower()

    async def test_create_delivery_order_invalid_pizza(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a delivery order with an invalid pizza."""
        order_data = {
            "service_type": "delivery",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "invalid_pizza",
                    "quantity": 1,
                }
            ],
            "delivery_address": "123 Main St",
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Pizza invalid_pizza not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_create_delivery_order_invalid_beer(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a delivery order with an invalid beer."""
        order_data = {
            "service_type": "delivery",
            "items": [
                {
                    "type": "beer",
                    "product_name": "invalid_beer",
                    "quantity": 1,
                }
            ],
            "delivery_address": "123 Main St",
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Beer invalid_beer not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_create_delivery_order_zero_quantity(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a delivery order with zero quantity.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.DELIVERY,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Pepperoni",
                    "quantity": 0,
                }
            ],
            "delivery_address": "123 Main St",
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 422
        assert "quantity" in response.text.lower()

    async def test_create_takeaway_order_invalid_pizza(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a takeaway order with an invalid pizza."""
        order_data = {
            "service_type": "takeaway",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "invalid_pizza",
                    "quantity": 1,
                }
            ],
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Pizza invalid_pizza not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_create_takeaway_order_invalid_beer(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a takeaway order with an invalid beer."""
        order_data = {
            "service_type": "takeaway",
            "items": [
                {
                    "type": "beer",
                    "product_name": "invalid_beer",
                    "quantity": 1,
                }
            ],
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Beer invalid_beer not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_create_takeaway_order_zero_quantity(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a takeaway order with zero quantity.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.TAKEAWAY,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Quattro Formaggi",
                    "quantity": 0,
                }
            ],
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 422
        assert "quantity" in response.text.lower()

    @freeze_time("2024-03-19 23:00:00")
    async def test_create_late_night_order_invalid_pizza(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a late night order with an invalid pizza."""
        order_data = {
            "service_type": "late_night",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "invalid_pizza",
                    "quantity": 1,
                }
            ],
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Pizza invalid_pizza not found"
            in response.json()["errors"][0]["details"]
        )

    @freeze_time("2024-03-19 23:00:00")
    async def test_create_late_night_order_invalid_beer(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a late night order with an invalid beer."""
        order_data = {
            "service_type": "late_night",
            "items": [
                {
                    "type": "beer",
                    "product_name": "invalid_beer",
                    "quantity": 1,
                }
            ],
        }
        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            "Beer invalid_beer not found"
            in response.json()["errors"][0]["details"]
        )

    @freeze_time("2024-03-19 23:00:00")
    async def test_create_late_night_order_zero_quantity(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating a late night order with zero quantity.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": ServiceType.LATE_NIGHT,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Diavola",
                    "quantity": 0,
                }
            ],
            "delivery_address": "456 Night St",
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 422
        assert "quantity" in response.text.lower()

    async def test_create_order_invalid_service_type(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test creating an order with invalid service type.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        order_data = {
            "service_type": "INVALID_SERVICE",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Margherita",
                    "quantity": 1,
                }
            ],
        }

        response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert response.status_code == 422
        assert "service_type" in response.text.lower()

    async def test_get_order_success(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test successfully retrieving an order.

        :param async_client: The async client
        :type async_client: AsyncClient
        """
        # First create an order
        order_data = {
            "service_type": ServiceType.DINE_IN,
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Margherita",
                    "quantity": 2,
                }
            ],
            "notes": "Extra cheese please",
        }

        create_response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert create_response.status_code == 201
        created_order = create_response.json()
        order_id = created_order["id"]

        # Now get the order
        get_response = await async_client.get(f"/v1/orders/{order_id}/")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == order_id
        assert data["service_type"] == ServiceType.DINE_IN
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "pizza"
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["price"] == "12.99"
        assert data["notes"] == "Extra cheese please"
        assert "created_at" in data
        assert "updated_at" in data

    async def test_get_order_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test getting a non-existent order."""
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await async_client.get(f"/v1/orders/{non_existent_id}/")
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"
        assert (
            f"Order {non_existent_id} not found"
            in response.json()["errors"][0]["details"]
        )

    async def test_update_dine_in_order_same_type(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a dine-in order with the same service type.

        Given: A dine-in order exists with initial items and notes
        When: The order is updated with new quantities and notes
        Then: The order should be updated successfully with the new values
        """
        # Given: A dine-in order exists
        order_data = {
            "service_type": "dine_in",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is updated
        update_data = {
            "service_type": "dine_in",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 2},
                {"type": "beer", "product_name": "Heineken", "quantity": 1},
            ],
            "notes": "Updated order",
            "status": "pending",
        }
        response = await async_client.patch(
            f"/v1/orders/{order_id}/", json=update_data
        )

        # Then: The order should be updated successfully
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["service_type"] == "dine_in"
        assert len(updated_order["items"]) == 2
        assert updated_order["notes"] == "Updated order"
        assert updated_order["status"] == "pending"
        # Check items
        pizza_item = next(
            item for item in updated_order["items"] if item["type"] == "pizza"
        )
        beer_item = next(
            item for item in updated_order["items"] if item["type"] == "beer"
        )
        assert pizza_item["quantity"] == 2
        assert beer_item["quantity"] == 1

    async def test_update_delivery_order_same_type(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a delivery order with the same service type.

        Given: A delivery order exists with initial items, notes and delivery address
        When: The order is updated with new quantities, notes and delivery address
        Then: The order should be updated successfully with the new values
        """
        # Given: A delivery order exists
        order_data = {
            "service_type": "delivery",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
            "delivery_address": "123 Main St",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is updated
        update_data = {
            "service_type": "delivery",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 2},
                {"type": "beer", "product_name": "Heineken", "quantity": 1},
            ],
            "notes": "Updated order",
            "status": "pending",
            "delivery_address": "456 Oak St",
        }
        response = await async_client.patch(
            f"/v1/orders/{order_id}/", json=update_data
        )

        # Then: The order should be updated successfully
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["service_type"] == "delivery"
        assert len(updated_order["items"]) == 2
        assert updated_order["notes"] == "Updated order"
        assert updated_order["status"] == "pending"
        assert updated_order["delivery_address"] == "456 Oak St"
        # Check items
        pizza_item = next(
            item for item in updated_order["items"] if item["type"] == "pizza"
        )
        beer_item = next(
            item for item in updated_order["items"] if item["type"] == "beer"
        )
        assert pizza_item["quantity"] == 2
        assert beer_item["quantity"] == 1

    async def test_update_takeaway_order_same_type(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a takeaway order with the same service type.

        Given: A takeaway order exists with initial items and notes
        When: The order is updated with new quantities and notes
        Then: The order should be updated successfully with the new values
        """
        # Given: A takeaway order exists
        order_data = {
            "service_type": "takeaway",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is updated
        update_data = {
            "service_type": "takeaway",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 2},
                {"type": "beer", "product_name": "Heineken", "quantity": 1},
            ],
            "notes": "Updated order",
            "status": "pending",
        }
        response = await async_client.patch(
            f"/v1/orders/{order_id}/", json=update_data
        )

        # Then: The order should be updated successfully
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["service_type"] == "takeaway"
        assert len(updated_order["items"]) == 2
        assert updated_order["notes"] == "Updated order"
        assert updated_order["status"] == "pending"
        # Check items
        pizza_item = next(
            item for item in updated_order["items"] if item["type"] == "pizza"
        )
        beer_item = next(
            item for item in updated_order["items"] if item["type"] == "beer"
        )
        assert pizza_item["quantity"] == 2
        assert beer_item["quantity"] == 1

    @freeze_time("2024-03-19 23:00:00")
    async def test_update_late_night_order_same_type(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a late night order with the same service type.

        Given: A late night order exists with initial items and notes
        When: The order is updated with new quantities and notes
        Then: The order should be updated successfully with the new values
        """
        # Given: A late night order exists
        order_data = {
            "service_type": "late_night",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is updated
        update_data = {
            "service_type": "late_night",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 2},
                {"type": "beer", "product_name": "Heineken", "quantity": 1},
            ],
            "notes": "Updated order",
            "status": "pending",
        }
        response = await async_client.patch(
            f"/v1/orders/{order_id}/", json=update_data
        )

        # Then: The order should be updated successfully
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["service_type"] == "late_night"
        assert len(updated_order["items"]) == 2
        assert updated_order["notes"] == "Updated order"
        assert updated_order["status"] == "pending"
        # Check items
        pizza_item = next(
            item for item in updated_order["items"] if item["type"] == "pizza"
        )
        beer_item = next(
            item for item in updated_order["items"] if item["type"] == "beer"
        )
        assert pizza_item["quantity"] == 2
        assert beer_item["quantity"] == 1

    async def test_update_dine_in_to_delivery(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a dine-in order to delivery.

        Given: A dine-in order exists
        When: An attempt is made to update it to a delivery order
        Then: The update should fail with a validation error
        """
        # Given: A dine-in order exists
        order_data = {
            "service_type": "dine_in",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Margherita",
                    "quantity": 2,
                }
            ],
            "notes": "Extra cheese please",
        }

        create_response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert create_response.status_code == 201
        created_order = create_response.json()
        order_id = created_order["id"]

        # When: An attempt is made to update it to a delivery order
        update_data = {
            "service_type": "delivery",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Margherita",
                    "quantity": 2,
                }
            ],
            "notes": "Extra cheese please",
            "delivery_address": "123 Main St",
            "status": "pending",
        }

        update_response = await async_client.patch(
            f"/v1/orders/{order_id}/",
            json=update_data,
        )

        # Then: The update should fail with a validation error
        assert update_response.status_code == 400
        assert (
            "Cannot change service type"
            in update_response.json()["errors"][0]["details"]
        )

    async def test_update_delivery_to_takeaway(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a delivery order to takeaway.

        Given: A delivery order exists
        When: An attempt is made to update it to a takeaway order
        Then: The update should fail with a validation error
        """
        # Given: A delivery order exists
        order_data = {
            "service_type": "delivery",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Pepperoni",
                    "quantity": 1,
                }
            ],
            "notes": "Ring the doorbell twice",
            "delivery_address": "123 Main St",
        }

        create_response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert create_response.status_code == 201
        created_order = create_response.json()
        order_id = created_order["id"]

        # When: An attempt is made to update it to a takeaway order
        update_data = {
            "service_type": "takeaway",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Pepperoni",
                    "quantity": 1,
                }
            ],
            "notes": "Ready in 20 minutes",
            "status": "pending",
        }

        update_response = await async_client.patch(
            f"/v1/orders/{order_id}/",
            json=update_data,
        )

        # Then: The update should fail with a validation error
        assert update_response.status_code == 400
        assert (
            "Cannot change service type"
            in update_response.json()["errors"][0]["details"]
        )

    @freeze_time("2024-03-19 23:00:00")
    async def test_update_takeaway_to_late_night(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a takeaway order to late night.

        Given: A takeaway order exists
        When: An attempt is made to update it to a late night order
        Then: The update should fail with a validation error
        """
        # Given: A takeaway order exists
        order_data = {
            "service_type": "takeaway",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Quattro Formaggi",
                    "quantity": 1,
                }
            ],
            "notes": "Ready in 20 minutes",
        }

        create_response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert create_response.status_code == 201
        created_order = create_response.json()
        order_id = created_order["id"]

        # When: An attempt is made to update it to a late night order
        update_data = {
            "service_type": "late_night",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Quattro Formaggi",
                    "quantity": 1,
                }
            ],
            "notes": "After hours delivery",
            "delivery_address": "456 Night St",
            "status": "pending",
        }

        update_response = await async_client.patch(
            f"/v1/orders/{order_id}/",
            json=update_data,
        )

        # Then: The update should fail with a validation error
        assert update_response.status_code == 400
        assert (
            "Cannot change service type"
            in update_response.json()["errors"][0]["details"]
        )

    @freeze_time("2024-03-19 23:00:00")
    async def test_update_late_night_to_dine_in(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test updating a late night order to dine-in.

        Given: A late night order exists
        When: An attempt is made to update it to a dine-in order
        Then: The update should fail with a validation error
        """
        # Given: A late night order exists
        order_data = {
            "service_type": "late_night",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Diavola",
                    "quantity": 1,
                }
            ],
            "notes": "After hours delivery",
            "delivery_address": "456 Night St",
        }

        create_response = await async_client.post(
            "/v1/orders/",
            json=order_data,
        )

        assert create_response.status_code == 201
        created_order = create_response.json()
        order_id = created_order["id"]

        # When: An attempt is made to update it to a dine-in order
        update_data = {
            "service_type": "dine_in",
            "items": [
                {
                    "type": "pizza",
                    "product_name": "Diavola",
                    "quantity": 1,
                }
            ],
            "notes": "Extra spicy please",
            "status": "pending",
        }

        update_response = await async_client.patch(
            f"/v1/orders/{order_id}/",
            json=update_data,
        )

        # Then: The update should fail with a validation error
        assert update_response.status_code == 400
        assert (
            "Cannot change service type"
            in update_response.json()["errors"][0]["details"]
        )

    async def test_cancel_dine_in_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a dine-in order.

        Given: A dine-in order exists
        When: The order is cancelled
        Then: The order should be cancelled successfully
        """
        # Given: A dine-in order exists
        order_data = {
            "service_type": "dine_in",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is cancelled
        response = await async_client.delete(
            f"/v1/orders/{order_id}/",
        )

        # Then: The order should be cancelled successfully
        assert response.status_code == 200
        cancelled_order = response.json()
        assert cancelled_order["status"] == "cancelled"
        assert cancelled_order["service_type"] == "dine_in"
        assert len(cancelled_order["items"]) == 2

    async def test_cancel_nonexistent_dine_in_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a non-existent dine-in order.

        Given: No order exists with the given ID
        When: An attempt is made to cancel the order
        Then: The request should fail with a not found error
        """
        # Given: No order exists with the given ID
        nonexistent_id = "00000000-0000-0000-0000-000000000000"

        # When: An attempt is made to cancel the order
        response = await async_client.delete(
            f"/v1/orders/{nonexistent_id}/",
        )

        # Then: The request should fail with a not found error
        assert response.status_code == 404
        assert "not found" in response.json()["errors"][0]["details"].lower()

    async def test_cancel_delivery_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a delivery order.

        Given: A delivery order exists
        When: The order is cancelled
        Then: The order should be cancelled successfully
        """
        # Given: A delivery order exists
        order_data = {
            "service_type": "delivery",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
            "delivery_address": "123 Main St",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is cancelled
        response = await async_client.delete(
            f"/v1/orders/{order_id}/",
        )

        # Then: The order should be cancelled successfully
        assert response.status_code == 200
        cancelled_order = response.json()
        assert cancelled_order["status"] == "cancelled"
        assert cancelled_order["service_type"] == "delivery"
        assert len(cancelled_order["items"]) == 2
        assert cancelled_order["delivery_address"] == "123 Main St"

    async def test_cancel_nonexistent_delivery_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a non-existent delivery order.

        Given: No order exists with the given ID
        When: An attempt is made to cancel the order
        Then: The request should fail with a not found error
        """
        # Given: No order exists with the given ID
        nonexistent_id = "00000000-0000-0000-0000-000000000000"

        # When: An attempt is made to cancel the order
        response = await async_client.delete(
            f"/v1/orders/{nonexistent_id}/",
        )

        # Then: The request should fail with a not found error
        assert response.status_code == 404
        assert "not found" in response.json()["errors"][0]["details"].lower()

    async def test_cancel_takeaway_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a takeaway order.

        Given: A takeaway order exists
        When: The order is cancelled
        Then: The order should be cancelled successfully
        """
        # Given: A takeaway order exists
        order_data = {
            "service_type": "takeaway",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is cancelled
        response = await async_client.delete(
            f"/v1/orders/{order_id}/",
        )

        # Then: The order should be cancelled successfully
        assert response.status_code == 200
        cancelled_order = response.json()
        assert cancelled_order["status"] == "cancelled"
        assert cancelled_order["service_type"] == "takeaway"
        assert len(cancelled_order["items"]) == 2

    async def test_cancel_nonexistent_takeaway_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a non-existent takeaway order.

        Given: No order exists with the given ID
        When: An attempt is made to cancel the order
        Then: The request should fail with a not found error
        """
        # Given: No order exists with the given ID
        nonexistent_id = "00000000-0000-0000-0000-000000000000"

        # When: An attempt is made to cancel the order
        response = await async_client.delete(
            f"/v1/orders/{nonexistent_id}/",
        )

        # Then: The request should fail with a not found error
        assert response.status_code == 404
        assert "not found" in response.json()["errors"][0]["details"].lower()

    @freeze_time("2024-03-19 23:00:00")
    async def test_cancel_late_night_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a late night order.

        Given: A late night order exists
        When: The order is cancelled
        Then: The order should be cancelled successfully
        """
        # Given: A late night order exists
        order_data = {
            "service_type": "late_night",
            "items": [
                {"type": "pizza", "product_name": "Margherita", "quantity": 1},
                {"type": "beer", "product_name": "Heineken", "quantity": 2},
            ],
            "notes": "Initial order",
        }
        response = await async_client.post("/v1/orders/", json=order_data)
        assert response.status_code == 201
        order_id = response.json()["id"]

        # When: The order is cancelled
        response = await async_client.delete(
            f"/v1/orders/{order_id}/",
        )

        # Then: The order should be cancelled successfully
        assert response.status_code == 200
        cancelled_order = response.json()
        assert cancelled_order["status"] == "cancelled"
        assert cancelled_order["service_type"] == "late_night"
        assert len(cancelled_order["items"]) == 2

    @freeze_time("2024-03-19 23:00:00")
    async def test_cancel_nonexistent_late_night_order(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test cancelling a non-existent late night order.

        Given: No order exists with the given ID
        When: An attempt is made to cancel the order
        Then: The request should fail with a not found error
        """
        # Given: No order exists with the given ID
        nonexistent_id = "00000000-0000-0000-0000-000000000000"

        # When: An attempt is made to cancel the order
        response = await async_client.delete(
            f"/v1/orders/{nonexistent_id}/",
        )

        # Then: The request should fail with a not found error
        assert response.status_code == 404
        assert "not found" in response.json()["errors"][0]["details"].lower()
