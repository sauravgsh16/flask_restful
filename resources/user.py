import traceback
from flask import request, make_response, render_template
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_refresh_token_required,
    jwt_required
)
from werkzeug.security import safe_str_cmp

from schemas.user import UserSchema
from models.user import UserModel
from lib.mailgun import MailgunException
from blacklist import BLACKLIST


user_schema = UserSchema()

class UserRegister(Resource):

    def post(self):
        user = user_schema.load(request.get_json())

        # Using flask-marshmallow, we no longer get a dict object. Instead, we
        # get an UserModel object when load is called. user_schema knows this
        # info, from the definition of UserSchema
        # prev : user = UserModel.find_by_name(user['username'])
        if UserModel.find_by_name(user.username):
            return {'message': 'A user with this username already exists'}, 400

        if UserModel.find_by_email(user.email):
            return {'message': 'A user with this email already exists'}, 400

        # or unpack as: UserModel(**data)
        
        # No need to create instance of UserModel
        # user = UserModel(data['username'], data['password'])
        try:
            user.save_to_db()
            user.send_confirmation_email()
        except MailgunException as err:
            user.delete_from_db()
            return {'message': str(err)}, 500
        except:
            traceback.print_exc()
            return {'message': 'Failed to create user'}, 500

        return {'message': 'We have sent you an email. Please confirm'}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user_schema.dump(user)

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        user.delete_from_db()
        return {'message': 'User deleted'}


class UserLogin(Resource):

    def post(self):
        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=('email',)) # partial tells marshmallow, that we can ignore email in request

        user = UserModel.find_by_name(user_data.username)

        if user and safe_str_cmp(user.password, user_data.password):
            if user.activated:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 200
            return {'message': 'User {} not confirmed'.format(user.username)}, 200
        return {'message': 'User credentials invalid'}, 401


class UserConfirm(Resource):

    @classmethod
    def get(cls, user_id: int):

        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        user.activated = True
        user.save_to_db()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('confirmation_page.html', email=user.email), 200, headers)


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
