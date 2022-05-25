"""Attune v5 Starting Point

Revision ID: 16e34a42a9a1
Revises: 
Create Date: 2022-03-16 15:26:28.813729

"""

# revision identifiers, used by Alembic.
from attune_project_api import ObjectStorageContext

revision = "16e34a42a9a1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade(storageContext: ObjectStorageContext):
    pass


def downgrade(storageContext: ObjectStorageContext):
    pass
