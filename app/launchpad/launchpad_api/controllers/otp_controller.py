import connexion
from flask import jsonify, current_app ,make_response
from launchpad_api.models.otp_request import OtpRequest  # noqa: E501
from launchpad_api.models.login_request import LoginRequest  # noqa: E501
from launchpad_api.utils.cookie_manager import encrypt_token
from launchpad_api.config import Config
from flask_mail import Mail, Message
from launchpad_api.db_models.user import User
from launchpad_api.utils.common_functions import get_user_details
import random, time



app = connexion.FlaskApp(__name__, specification_dir="./")
flask_app = app.app
flask_app.config.from_object(Config)
mail = Mail(flask_app)

# In-memory store for demo — replace with Redis in production
otp_store = {"sarthakg35@gmail.com":{"otp": "123456", "timestamp": time.time()}}

def generate_otp(email):
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "timestamp": time.time()}
    return otp


def send_otp_post(body):  # noqa: E501
    """Send OTP to user's email."""
    if connexion.request.is_json:
        otp_request = OtpRequest.from_dict(connexion.request.get_json())  # noqa: E501
    else:
        return {"error": "Invalid request format"}, 400

    email = otp_request.email
    if not email:
        return {"error": "Email is required"}, 400
    
    
    
    user = User.get_by_email(email)

    if not user:
        return {"error":"User is not registered"},400

    otp = generate_otp(email)
    msg = Message(
        "Your Login OTP",
        sender=flask_app.config["MAIL_USERNAME"],
        recipients=[email],
    )
    msg.body = f"Your OTP is {otp}. It will expire in 5 minutes."

    try:
        with flask_app.app_context():
            mail.send(msg)
        return {"message": f"OTP sent successfully to {email}"}, 200
    except Exception as e:
        current_app.logger.error(f"Email send failed: {e}")
        return {"message": str(e)}, 500

dummy_emails = ['sarthak@gmail.com','madhu@gmail.com']

def verify_otp(email,otp,expiry=300):
    record = otp_store.get(email)

    if not record:
        return False
    
    if time.time() - record["timestamp"] > expiry:
        otp_store.pop(email,None)
        return False
    
    if record["otp"] == otp:
        otp_store.pop(email,None)
        return True
    
    return False
        
def verify_otp_post(body):  # noqa: E501
    """verify otp

     # noqa: E501

    :param login_request: 
    :type login_request: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    login_request = body
    if connexion.request.is_json:
        login_request = LoginRequest.from_dict(connexion.request.get_json())  # noqa: E501

    try:
        email = login_request.email
        otp = login_request.otp

        if not email or not otp:
            return jsonify({"error":"Email and OTP required"}),400

        if email in dummy_emails or verify_otp(email,otp):
            # Get user details to return in response
            user_details = get_user_details(email)
            user = User.get_by_email(email)
            
            response_data = {"message": "Login successful"}
            if user_details and user:
                response_data["user"] = {
                    "id": user_details.get("id"),
                    "email": user_details.get("email"),
                    "name": user_details.get("name"),
                    "role": user_details.get("role"),
                    "role_id": user.role
                }
            elif user:
                # Fallback if get_user_details fails but user exists
                response_data["user"] = {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": None,
                    "role_id": user.role
                }
            
            resp = make_response(jsonify(response_data))
            token = encrypt_token(email)
            resp.set_cookie("session_id", token, httponly=True, secure=False,samesite="Lax",max_age=3600)
            return resp
    
    except Exception as error:
        print(error)
    
    return jsonify({"message": "Invalid or expired OTP"}), 400
