import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Achievements(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'achievements'

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), primary_key=True)
    success = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    total = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
