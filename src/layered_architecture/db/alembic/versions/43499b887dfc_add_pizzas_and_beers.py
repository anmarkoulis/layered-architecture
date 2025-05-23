"""Add pizzas and beers.

Revision ID: 43499b887dfc
Revises: 9f884617fc52
Create Date: 2024-03-19 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "43499b887dfc"  # pragma: allowlist secret
down_revision: Union[str, None] = "216322cca0a8"  # pragma: allowlist secret
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert pizzas
    op.execute(
        """
        INSERT INTO pizza (id, name, description, price, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'Margherita', 'Classic tomato sauce, mozzarella, fresh basil', 12.99, NOW(), NOW()),
            (gen_random_uuid(), 'Pepperoni', 'Tomato sauce, mozzarella, spicy pepperoni', 14.99, NOW(), NOW()),
            (gen_random_uuid(), 'Quattro Formaggi', 'Four cheese blend: mozzarella, gorgonzola, parmesan, ricotta', 16.99, NOW(), NOW()),
            (gen_random_uuid(), 'Prosciutto e Funghi', 'Tomato sauce, mozzarella, prosciutto, mushrooms', 17.99, NOW(), NOW()),
            (gen_random_uuid(), 'Marinara', 'Tomato sauce, garlic, oregano, extra virgin olive oil', 11.99, NOW(), NOW()),
            (gen_random_uuid(), 'Vegetariana', 'Tomato sauce, mozzarella, bell peppers, mushrooms, onions, olives', 15.99, NOW(), NOW()),
            (gen_random_uuid(), 'Diavola', 'Tomato sauce, mozzarella, spicy salami, chili peppers', 15.99, NOW(), NOW()),
            (gen_random_uuid(), 'Capricciosa', 'Tomato sauce, mozzarella, ham, mushrooms, artichokes, olives', 16.99, NOW(), NOW()),
            (gen_random_uuid(), 'Quattro Stagioni', 'Tomato sauce, mozzarella, ham, mushrooms, artichokes, olives, eggs', 17.99, NOW(), NOW()),
            (gen_random_uuid(), 'Napoli', 'Tomato sauce, mozzarella, anchovies, capers, olives', 16.99, NOW(), NOW())
    """
    )

    # Insert beers
    op.execute(
        """
        INSERT INTO beer (id, name, brand, price, is_tap, created_at, updated_at)
        VALUES
            -- Bottled Beers
            (gen_random_uuid(), 'Peroni Nastro Azzurro', 'Peroni', 5.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Moretti', 'Birra Moretti', 5.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Corona Extra', 'Corona', 6.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Heineken', 'Heineken', 5.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Stella Artois', 'Stella Artois', 6.49, false, NOW(), NOW()),
            (gen_random_uuid(), 'Guinness Draught', 'Guinness', 7.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Hoegaarden', 'Hoegaarden', 6.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Leffe Blonde', 'Leffe', 7.49, false, NOW(), NOW()),
            (gen_random_uuid(), 'Chimay Blue', 'Chimay', 9.99, false, NOW(), NOW()),
            (gen_random_uuid(), 'Duvel', 'Duvel', 8.99, false, NOW(), NOW()),
            -- Tap Beers
            (gen_random_uuid(), 'Pilsner Urquell', 'Pilsner Urquell', 6.99, true, NOW(), NOW()),
            (gen_random_uuid(), 'Kozel Dark', 'Kozel', 7.49, true, NOW(), NOW()),
            (gen_random_uuid(), 'Staropramen', 'Staropramen', 6.49, true, NOW(), NOW()),
            (gen_random_uuid(), 'Budweiser Budvar', 'Budweiser', 6.99, true, NOW(), NOW()),
            (gen_random_uuid(), 'Krombacher', 'Krombacher', 6.49, true, NOW(), NOW())
    """
    )


def downgrade() -> None:
    pass
