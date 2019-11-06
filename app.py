from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError

from resources.user import (
    UserRegister,
    User,
    UserLogin,
    UserLogout,
    TokenRefresh
)
from resources.item import Items, Item
from resources.store import Store, Stores
from resources.confirmation import Confirmation, ConfirmationByUser
from blacklist import BLACKLIST
from ma import ma


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# Turns off the flask sqlalchemy modification tracker
# But does not turn of the sqlalchemy modification tracker, which is better
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Allows exception from flask extensions to be propogated
app.config['PROPOGATE_EXCEPTION'] = True
# Blacklist configs
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.secret_key = 'topsecret'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify({
        'description': err.messages,
        'error': 'Validation Error'
    }), 400

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:  # Generally query database, to check user is admin
        return {'is_admin': True}
    return {'is_admin': False}


# Function returns true if token sent is in blacklist
@jwt.token_in_blacklist_loader
def check_token_blacklisted(decrypted_token):
    # decrypted_token gets sent to this function.
    # the values of decrypted token gets set internally by jwt
    return decrypted_token['jti'] in BLACKLIST


# Triggered when token expired
@jwt.expired_token_loader
def exprired_token_callback():
    return jsonify({
        'descrption': 'Token had expired',
        'error': 'token_expired'
    }), 401


# Triggered when token in not valid JWT
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Invalid JWT token format',
        'error': 'invalid_token'
    }), 401


# Triggered with no access token is supplied
@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        'description': 'Request does not contain access token',
        'error': 'unauthorized_token'
    }), 401


# Triggered when token is not fresh and endpoint required fresh token
@jwt.needs_fresh_token_loader
def fresh_token_callback():
    return jsonify({
        'description': 'The token is not fresh',
        'error': 'not_fresh_token'
    }), 401


# Triggered when token is added to the blacklist
@jwt.revoked_token_loader
def revoked_token_called():
    return jsonify({
        'description': 'The token has been revoked',
        'error': 'token_revoked'
    }), 401


api.add_resource(Items, '/items')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(Stores, '/stores')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(Confirmation, '/user_confirmation/<string:confirmation_id>')
api.add_resource(ConfirmationByUser, '/confirmation/user/<int:user_id>')



if __name__ == '__main__':
    from db import db
    db.init_app(app)
    ma.init_app(app) # Attach flask-marshmallow to current app
    app.run(port=5000, debug=True)
