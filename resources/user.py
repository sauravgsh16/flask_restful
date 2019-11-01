import sqlite3
from models.user import UserModel
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
    get_raw_jwt
)
from werkzeug.security import safe_str_cmp

from blacklist import BLACKLIST


_parser = reqparse.RequestParser()
_parser.add_argument(
    'username',
    type=str,
    required=True,
    help='This field cannot be left blank'
)
_parser.add_argument(
    'password',
    type=str,
    required=True,
    help='This field cannot be left blank'
)


class UserRegister(Resource):

    def post(self):
        data = _parser.parse_args()

        user = UserModel.find_by_name(data['username'])
        if user:
            return {'message': 'A user with this username already exists'}, 400

        # or unpack as: UserModel(**data)
        user = UserModel(data['username'], data['password'])
        user.save_to_db()

        return {'message': 'Successfully created user'}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        user.delete_from_db()
        return {'message': 'User deleted'}


class UserLogin(Resource):

    def post(self):
        data = _parser.parse_args()

        user = UserModel.find_by_name(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            fresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'fresh_token': fresh_token
            }, 200
        return {'message': 'User credentials invalid'}, 401


class UserLogout(Resource):

    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # unique identifier for a jwt
        BLACKLIST.add(jti)
        return {'message': 'User logged out successfully'}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        # We can get the identity, since this part of the code will only get
        # executed, if we get a refresh token in the header
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
