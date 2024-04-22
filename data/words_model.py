import sqlalchemy

from .db_session import SqlAlchemyBase


class Nouns(SqlAlchemyBase):
    __tablename__ = 'nouns'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.String)


class Verbs(SqlAlchemyBase):
    __tablename__ = 'verbs'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.String)


class Adjectives(SqlAlchemyBase):
    __tablename__ = 'adjectives'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word = sqlalchemy.Column(sqlalchemy.String)
