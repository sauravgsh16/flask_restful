import sqlite3
from models.user import UserModel
from flask_restful import Resource, reqparse


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'username',
        type=str,
        required=True,
        help='This field cannot be left blank'
    )
    parser.add_argument(
        'password',
        type=str,
        required=True,
        help='This field cannot be left blank'
    )

    def post(self):
        data = UserRegister.parser.parse_args()

        user = UserModel.find_by_name(data['username'])
        if user:
            return {'message': 'A user with this username already exists'}, 400

        # or unpack as: UserModel(**data)
        user = UserModel(data['username'], data['password'])
        user.save_to_db()

        return {'message': 'Successfully created user'}, 201
