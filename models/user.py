import re
from flask import request, url_for
from requests import Response, post

from db import db
from lib.mailgun import Mailgun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    confirmation = db.relationship(
        'ConfirmationModel',
        lazy='dynamic', # when a new UserModel, confirmation is not created from the db, When we access confirmation property, it then goes to the db to retrive it.
        cascade='all, delete-orphan' #
    )

    # Thus for lazy dynamic, we can do the below
    # Create a user model user = UserModel(...)
    # create confirmation model confirm = ConfirmationModel()
    # confirm.save_to_db()
    # user.confirmation() # We can retrieve it from the db later

    # cascade 'all delete-orphan'
    # when we delete a user, all user details in the confirmation will be deleted also.
    # Does not work in all db, work in postgreSQL.

    @property
    def most_recent_confirmation(self):
        return self.confirmation.order_by(
            db.desc(ConfirmationModel.expire_at)
            ).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_name(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def send_confirmation_email(self) -> Response:
        pat = re.compile(r'(?P<ROOT>^.*)\/')
        root = pat.match(request.url_root).group('ROOT')
        link = root + url_for(
            'confirmation', # This is the name of the confirmation Resource - Confirmation
            confirmation_id=self.most_recent_confirmation.id
        )
        subject = "Registration Confirmation"
        text = f"Please click the link to confirm your registration: {link}"
        html =f'<html>Please click the link to confirm you registration <a href="{link}">{link}</a></html>'

        return Mailgun.send_email(self.email, subject, text, html)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
