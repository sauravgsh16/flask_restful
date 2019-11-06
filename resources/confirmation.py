import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from models.confirmation import ConfirmationModel
from schemas.confirmation import ConfirmationSchema
from lib.mailgun import MailgunException


confirmation_schema = ConfirmationSchema()

class Confirmation(Resource):

    @classmethod
    def get(cls, confirmation_id):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {'message': 'Not found'}, 404

        if confirmation.expired:
            return {'message': 'Confirmation expired'}, 400

        if confirmation.confirmed:
            return {'message': 'Registration already confirmed'}, 200

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {'Content-Type': 'text/html'}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers
        )


class ConfirmationByUser(Resource):

    @classmethod
    def get(cls, user_id):
        """ Used only for testing """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not find'}, 404

        return (
            {
                'current_time': int(time()),
                'confirmation': [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.exprire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {'message': 'Already confirmed'}, 400
                confirmation.force_exprire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {'message': 'Confirmation email resent'}, 201
        except MailgunException as err:
            return {'message': str(e)}, 500
        except:
            traceback.print_exc()
            return {'message': 'Failed to resend confirmation'}, 500
