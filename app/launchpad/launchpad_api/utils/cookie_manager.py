from flask import current_app
import jwt
import datetime



def encrypt_token(email):
    """
    Create a signed JWT token with email and 24-hour expiry.
    """
    token = jwt.encode({
        'user': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return token


def decrypt_token(token):
    """
    Decode and validate JWT. Return user email if valid.
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('user')
    except jwt.ExpiredSignatureError:
        print("Token expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None
