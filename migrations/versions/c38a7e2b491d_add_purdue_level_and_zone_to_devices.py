"""Add Purdue level and zone to devices

Revision ID: c38a7e2b491d
Revises: a1d5f86dea88
Create Date: 2026-10-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c38a7e2b491d"
down_revision = "a1d5f86dea88"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("devices", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "purdue_level",
                sa.String(length=10),
                nullable=False,
                server_default="Unassigned",
            )
        )
        batch_op.add_column(
            sa.Column(
                "zone",
                sa.String(length=100),
                nullable=False,
                server_default="Unassigned",
            )
        )


def downgrade():
    with op.batch_alter_table("devices", schema=None) as batch_op:
        batch_op.drop_column("zone")
        batch_op.drop_column("purdue_level")
