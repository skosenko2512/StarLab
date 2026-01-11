"""add endpoint metrics table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "11_01_2026_add_metrics_table"
down_revision = "10_01_2026_create_rates_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "endpoint_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("method", sa.String(length=8), nullable=False),
        sa.Column("path", sa.String(length=128), nullable=False),
        sa.Column("duration_ms", sa.Numeric(12, 4), nullable=False),
    )
    op.create_index(
        "idx_endpoint_metrics_path_method",
        "endpoint_metrics",
        ["path", "method"],
    )


def downgrade() -> None:
    op.drop_index("idx_endpoint_metrics_path_method", table_name="endpoint_metrics")
    op.drop_table("endpoint_metrics")
