from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f5b3c8d2a1e4"
down_revision: Union[str, Sequence[str], None] = "e4febd4a32e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add s3_audio_key column
    op.add_column("sessions", sa.Column("s3_audio_key", sa.String(), nullable=True))

    # Alter columns to be nullable (if they exist as NOT NULL)
    op.alter_column(
        "sessions",
        "session_duration_minutes",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.alter_column("sessions", "job_id", existing_type=sa.String(), nullable=True)

    op.alter_column(
        "sessions",
        "audio_metadata",
        existing_type=sa.dialects.postgresql.JSONB(),
        nullable=True,
    )

    op.alter_column(
        "sessions",
        "summary",
        existing_type=sa.dialects.postgresql.JSONB(),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove s3_audio_key column
    op.drop_column("sessions", "s3_audio_key")

    # Revert columns to NOT NULL (may fail if data contains NULLs)
    op.alter_column(
        "sessions",
        "session_duration_minutes",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column("sessions", "job_id", existing_type=sa.String(), nullable=False)

    op.alter_column(
        "sessions",
        "audio_metadata",
        existing_type=sa.dialects.postgresql.JSONB(),
        nullable=False,
    )

    op.alter_column(
        "sessions",
        "summary",
        existing_type=sa.dialects.postgresql.JSONB(),
        nullable=False,
    )
