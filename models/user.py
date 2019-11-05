import re
from flask import request, url_for
from requests import Response, post

from db import db
from lib.mailgun import Mailgun


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    activated = db.Column(db.Boolean, default=False)

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
        link = root + url_for('userconfirm', user_id=self.id)
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
