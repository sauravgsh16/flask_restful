from flask import g, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from auth import github

from models.user import UserModel

class GithubLogin(Resource):

    @classmethod
    def get(cls):
        return github.authorize(callback="http://localhost:5000/login/github/authorized")


class GithubAuthorize(Resource):

    @classmethod
    def get(cls):
        resp = github.authorized_response()

        if resp is None or resp.get('access_token') is None:
            error_resp = {
                "error": request.args["error"],
                "error_description": request.args["error_description"]
            }
            return error_resp

        g.access_token = resp['access_token'] # save the access token in the context of the request
        github_user = github.get('user') # get the user from the request context
        github_username = github_user.data['login'] # saves the user info in data. username is stored with login key
        
        user = UserModel.find_by_name(github_username)

        if not user:
            user = UserModel(username=github_username, password=None)
            user.save_to_db()
        
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)

        # TODO: NEED TO ADD LOGIC TO SEND USER CONFIRMATION EMAIL

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200
