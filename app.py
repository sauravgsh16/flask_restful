from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, TokenRefresh
from resources.item import Items, Item
from resources.store import Store, Stores


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# Turns off the flask sqlalchemy modification tracker
# But does not turn of the sqlalchemy modification tracker, which is better
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Allows exception from flask extensions to be propogated
app.config['PROPOGATE_EXCEPTION'] = True

app.secret_key = 'topsecret'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


api.add_resource(Items, '/items')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(Stores, '/stores')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
