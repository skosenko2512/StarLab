"""create rates tables"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "10_01_2026_create_rates_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auto_rates",
        sa.Column("currency_code", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("currency_type", sa.String(length=8), nullable=False),
        sa.Column("rate_to_rub", sa.Numeric(18, 6), nullable=False),
        sa.PrimaryKeyConstraint("currency_code"),
        sa.UniqueConstraint("currency_type"),
    )
    op.create_table(
        "manual_rates",
        sa.Column("currency_code", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("currency_type", sa.String(length=8), nullable=False),
        sa.Column("rate_to_rub", sa.Numeric(18, 6), nullable=False),
        sa.PrimaryKeyConstraint("currency_code"),
        sa.UniqueConstraint("currency_type"),
    )


def downgrade() -> None:
    op.drop_table("manual_rates")
    op.drop_table("auto_rates")
