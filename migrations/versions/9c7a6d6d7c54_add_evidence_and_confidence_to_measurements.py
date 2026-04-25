"""add_evidence_and_confidence_to_measurements

Revision ID: 9c7a6d6d7c54
Revises: 9000c38b6fd1
Create Date: 2026-04-25 21:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c7a6d6d7c54"
down_revision: Union[str, Sequence[str], None] = "9000c38b6fd1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FIELD_MAP = {
    "foodvolume": [
        "kg_received_total",
        "kg_via_national_dc",
        "kg_direct",
        "waste_pct",
        "parcels_distributed",
        "avg_products_per_parcel",
        "pct_schijf_van_vijf",
        "food_value_eur",
        "kg_non_food",
    ],
    "foodcategories": [
        "kg_produce",
        "kg_meat_fish",
        "kg_dairy_eggs",
        "kg_dry_goods",
        "kg_bread_bakery",
        "kg_prepared",
    ],
    "peopleserved": [
        "households_weekly",
        "individuals_total",
        "children_count",
        "pct_under_18",
        "pct_single_adults",
        "pct_single_parent",
        "pct_families",
        "pct_couples",
    ],
    "operations": [
        "volunteers_count",
        "distribution_locations",
        "satellite_banks_served",
        "annual_budget_eur",
        "total_expenditure_eur",
    ],
    "donations": [
        "food_supermarket_kg",
        "food_company_kg",
        "food_dc_kg",
        "money_individuals_eur",
        "money_companies_eur",
        "money_orgs_eur",
        "money_government_eur",
    ],
}


def upgrade() -> None:
    for table_name, fields in FIELD_MAP.items():
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            for field in fields:
                batch_op.add_column(
                    sa.Column(f"{field}_evidence", sa.String(length=1000), nullable=True)
                )
                batch_op.add_column(
                    sa.Column(f"{field}_confidence", sa.Float(), nullable=True)
                )


def downgrade() -> None:
    for table_name, fields in FIELD_MAP.items():
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            for field in reversed(fields):
                batch_op.drop_column(f"{field}_confidence")
                batch_op.drop_column(f"{field}_evidence")
