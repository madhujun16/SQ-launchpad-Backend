from flask import Flask, request, jsonify, g
from werkzeug.exceptions import Unauthorized

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'replace-with-strong-secret'

    @app.before_request
    def check_auth():
        # Skip login endpoint
        if request.endpoint == 'app.controllers.login_controller.login_post':
            return
        # Check cookie
        session_id = request.cookies.get('session_id')
        if not session_id or not validate_session(session_id):
            raise Unauthorized("Invalid or missing session cookie")

    def validate_session(session_id):
        # TODO: connect to redis or database
        return session_id == "demo-session"

    return app
