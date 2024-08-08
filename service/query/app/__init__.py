from flask import Flask
from .routes import main

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object('config.Config')

    # Register blueprints
    app.register_blueprint(main)

    # Additional setup can be done here, e.g., initializing database connections

    return app
