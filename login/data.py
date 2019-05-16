import os
import base64
import onetimepass
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(500))
    last_name = db.Column(db.String(500))
    password = db.Column(db.String(100))
    otp_secret = db.Column(db.String(16))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:

            """
            Generate a random secret string
            """
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    """
    Get the authentication URI. This URI will be rendered
    as a QR code
    """
    def get_totp_uri(self):
        return 'otpauth://totp/Flask-2FA:{0}?secret={1}&issuer=Flask-2FA'.format(self.email, self.otp_secret)

    """
    Validate the token using the onetimepass package, which
    generates one-time passwords
    """
    def verify_totp(self, auth_code):
        return onetimepass.valid_totp(auth_code, self.otp_secret)
