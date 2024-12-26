"""Add qr_code_img column to ShortenedURL

Revision ID: 4fe83550c71b
Revises: 
Create Date: 2024-12-26 14:33:39.611115

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fe83550c71b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shortened_url', schema=None) as batch_op:
        batch_op.add_column(sa.Column('qr_code_img', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shortened_url', schema=None) as batch_op:
        batch_op.drop_column('qr_code_img')

    # ### end Alembic commands ###