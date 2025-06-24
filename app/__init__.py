from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'aladint007-010montext'

    from .routes import main
    app.register_blueprint(main)

    return app
