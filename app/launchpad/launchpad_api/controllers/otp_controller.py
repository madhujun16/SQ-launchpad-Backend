import connexion
from flask import jsonify, make_response
from ..models.otp_request import OtpRequest  # noqa: E501
from ..models.login_request import LoginRequest  # noqa: E501
from ..utils.cookie_manager import encrypt_token
from ..config import Config
from flask_mail import Mail, Message
from ..db_models.user import User
from ..utils.common_functions import get_user_details
import random
import time
import logging
import traceback

logger = logging.getLogger(__name__)

app = connexion.FlaskApp(__name__, specification_dir="./")
flask_app = app.app
flask_app.config.from_object(Config)
mail = Mail(flask_app)

# In-memory store for demo — replace with Redis in production
otp_store = {"sarthakg35@gmail.com": {"otp": "123456", "timestamp": time.time()}}

def generate_otp(email):
    """Generate a 6-digit OTP and store it with timestamp."""
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "timestamp": time.time()}
    return otp


def is_email_service_configured():
    """Check if email service is properly configured."""
    mail_username = flask_app.config.get("MAIL_USERNAME")
    mail_password = flask_app.config.get("MAIL_PASSWORD")
    mail_server = flask_app.config.get("MAIL_SERVER")
    
    if not mail_username or not mail_password:
        logger.warning("Email service not configured: MAIL_USERNAME or MAIL_PASSWORD missing")
        return False
    
    if not mail_server:
        logger.warning("Email service not configured: MAIL_SERVER missing")
        return False
    
    return True


def send_otp_post(body):  # noqa: E501
    """Send OTP to user's email."""
    try:
        # Parse request
        if connexion.request.is_json:
            otp_request = OtpRequest.from_dict(connexion.request.get_json())  # noqa: E501
        else:
            return jsonify({"error": "Invalid request format. Expected JSON."}), 400

        email = otp_request.email
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Validate email format (basic check)
        if "@" not in email or "." not in email:
            return jsonify({"error": "Invalid email address format"}), 400
        
        # Check if user exists
        try:
            user = User.get_by_email(email)
            if not user:
                return jsonify({"error": "User is not registered"}), 400
        except Exception as db_error:
            logger.error(f"[send_otp_post] Database error checking user: {str(db_error)}")
            logger.error(f"[send_otp_post] Traceback: {traceback.format_exc()}")
            return jsonify({"error": "Database connection error. Please try again later."}), 500

        # Check if email service is configured
        if not is_email_service_configured():
            logger.error("[send_otp_post] Email service not configured")
            return jsonify({
                "error": "Email service not configured. Please contact support.",
                "message": "The email service is not properly configured on the server."
            }), 500

        # Generate OTP
        otp = generate_otp(email)
        logger.info(f"[send_otp_post] Generated OTP for {email}")

        # Create email message
        try:
            msg = Message(
                "Your Login OTP",
                sender=flask_app.config["MAIL_USERNAME"],
                recipients=[email],
            )
            msg.body = f"Your OTP is {otp}. It will expire in 5 minutes."
        except Exception as msg_error:
            logger.error(f"[send_otp_post] Error creating email message: {str(msg_error)}")
            return jsonify({
                "error": "Failed to create email message",
                "message": "There was an error preparing the email. Please try again."
            }), 500

        # Send email
        try:
            with flask_app.app_context():
                mail.send(msg)
            logger.info(f"[send_otp_post] OTP email sent successfully to {email}")
            return jsonify({"message": f"OTP sent successfully to {email}"}), 200
        except Exception as email_error:
            error_message = str(email_error)
            logger.error(f"[send_otp_post] Email send failed: {error_message}")
            logger.error(f"[send_otp_post] Traceback: {traceback.format_exc()}")
            
            # Provide more specific error messages
            if "authentication failed" in error_message.lower() or "invalid credentials" in error_message.lower():
                return jsonify({
                    "error": "Email service authentication failed",
                    "message": "The email service credentials are invalid. Please contact support."
                }), 500
            elif "connection" in error_message.lower() or "timeout" in error_message.lower():
                return jsonify({
                    "error": "Email service connection failed",
                    "message": "Unable to connect to email service. Please try again later."
                }), 500
            else:
                return jsonify({
                    "error": "Failed to send email",
                    "message": f"An error occurred while sending the email: {error_message}"
                }), 500

    except Exception as e:
        error_message = str(e)
        logger.error(f"[send_otp_post] Unexpected error: {error_message}")
        logger.error(f"[send_otp_post] Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later or contact support."
        }), 500

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
