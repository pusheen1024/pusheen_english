import sqlalchemy
from flask import jsonify
from flask_restful import reqparse, abort, Resource

from . import db_session
from .users_model import User
from .achievements_model import Achievements

parser = reqparse.RequestParser()
parser.add_argument('success', type=int, required=True)


def abort_if_user_not_found(email):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        abort(404, message=f'User with email {email} not found')    


class AchievementsResource(Resource):
    def get(self, email):
        abort_if_user_not_found(email)
        session = db_session.create_session()
        user = session.query(User).filter(User.email == email).first()
        achievements = session.query(Achievements).get(user.id)
        return jsonify(achievements.to_dict())

    def post(self, email):
        args = parser.parse_args()
        abort_if_user_not_found(email)
        session = db_session.create_session()
        user = session.query(User).filter(User.email == email).first()
        achievements = session.query(Achievements).get(user.id)
        achievements.success += args['success']
        achievements.total += 1
        session.commit()
        return jsonify({'id': user.id})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        api_fields = ['id', 'name', 'surname', 'email', 'age', 'like_english']
        return jsonify({'users': [item.to_dict(only=api_fields) for item in users]})
