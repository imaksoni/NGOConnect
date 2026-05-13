"""Add full text search indexes

Revision ID: 66f440cd795a
Revises: a6f38cae90a3
Create Date: 2026-05-13 11:20:05.008244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66f440cd795a'
down_revision: Union[str, Sequence[str], None] = 'a6f38cae90a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if bind.engine.name == 'postgresql':
        op.execute("""
            CREATE INDEX idx_ngos_search ON ngos USING GIN
            (to_tsvector('english', name || ' ' || slug || ' ' || coalesce(about, '')));
        """)
        op.execute("""
            CREATE INDEX idx_groups_search ON groups USING GIN
            (to_tsvector('english', name || ' ' || slug || ' ' || coalesce(about, '')));
        """)
        op.execute("""
            CREATE INDEX idx_events_search ON events USING GIN
            (to_tsvector('english', title || ' ' || coalesce(description, '') || ' ' || coalesce(location, '')));
        """)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    if bind.engine.name == 'postgresql':
        op.execute("DROP INDEX IF EXISTS idx_ngos_search;")
        op.execute("DROP INDEX IF EXISTS idx_groups_search;")
        op.execute("DROP INDEX IF EXISTS idx_events_search;")
