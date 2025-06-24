from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'aladint007-010montext'  # Secret key for session management

    from .routes import main
    app.register_blueprint(main)

    return app
