from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.secret_key = 'aladint007-010montext'

    # Configure server-side sessions
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False  # Sessions expires when the browser is closed
    app.config['SESSION_USE_SIGNER'] = True  # Sign the session cookies for security-purpose

    # Initialize the session's extension
    Session(app)

    from .routes import main
    app.register_blueprint(main)

    return app
