"""Add default tools

Revision ID: 49ff84a100e8
Revises: c13ac1b320b7
Create Date: 2020-07-29 14:40:01.099328

"""
from sqlalchemy import String
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision = "49ff84a100e8"
down_revision = "c13ac1b320b7"
branch_labels = None
depends_on = None


def upgrade():
    # define ad-hoc table for bulk_insert
    # we must not use the metadata from db.models as it might change in the future
    tools_table = table("tools", column("name", String))

    op.bulk_insert(
        tools_table,
        [
            {"name": "jira"},
            {"name": "git"},
            {"name": "slack"},
            {"name": "confluence"},
            {"name": "skype"},
            {"name": "microsoft-teams"},
        ],
    )


def downgrade():
    pass
