"""patch to user model

Revision ID: 68679b0ec53a
Revises: 2cfffc6cc495
Create Date: 2018-03-01 18:15:03.661194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68679b0ec53a'
down_revision = '2cfffc6cc495'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hash', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'password_hash')
    # ### end Alembic commands ###
