"""updated the opportunity table to have a col called opportunity type

Revision ID: 50fc4335a7eb
Revises: 
Create Date: 2025-12-12 00:39:54.858350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '50fc4335a7eb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the new ENUM type for OpportunityType
    opportunity_type = postgresql.ENUM('FULL_TIME', 'INTERNSHIP', 'RESEARCH', name='opportunitytype')
    opportunity_type.create(op.get_bind())

    # Add the 'type' column to the 'opportunities' table
    op.add_column(
        'opportunities',
        sa.Column('type', sa.Enum('FULL_TIME', 'INTERNSHIP', 'RESEARCH', name='opportunitytype'),
                  nullable=True, default='FULL_TIME')
    )
    op.execute("UPDATE opportunities SET type = 'FULL_TIME' WHERE type IS NULL")
    op.alter_column('opportunities', 'type', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the 'type' column from the 'opportunities' table
    op.drop_column('opportunities', 'type')

    # Drop the ENUM type
    opportunity_type = postgresql.ENUM('FULL_TIME', 'INTERNSHIP', 'RESEARCH', name='opportunitytype')
    opportunity_type.drop(op.get_bind())