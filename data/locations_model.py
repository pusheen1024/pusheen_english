import sqlalchemy

from .db_session import SqlAlchemyBase


class Location(SqlAlchemyBase):
    __tablename__ = 'locations'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    toponym = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)
