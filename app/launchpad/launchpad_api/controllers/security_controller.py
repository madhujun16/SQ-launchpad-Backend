from flask import request
from connexion.exceptions import OAuthProblem
from jwt import ExpiredSignatureError, InvalidTokenError
from ..utils.cookie_manager import decrypt_token
from ..utils.common_functions import get_user_details


def info_from_cookieAuth(api_key, required_scopes):
    """
    Connexion security handler for cookie-based authentication.
    Validates the 'session_id' cookie and returns user info if valid.
    """

    # 1️⃣ Get cookie from the incoming request
    token = request.cookies.get("session_id")
    if not token:
        raise OAuthProblem("Missing access_token cookie")

    try:
        # 2️⃣ Decrypt and validate JWT token
        email = decrypt_token(token)
        if not email:
            raise OAuthProblem("Invalid or expired access_token")
        
        # user_details = get_user_details(email)

        # if not user_details:
        #     raise OAuthProblem("User not found")
        
        return {}

    except ExpiredSignatureError:
        raise OAuthProblem("Token expired")
    except InvalidTokenError:
        raise OAuthProblem("Invalid token")
    except Exception as e:
        print(f"Unexpected error verifying token: {e}")
        raise OAuthProblem("Authentication error")
