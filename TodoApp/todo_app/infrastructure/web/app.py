
from flask import Flask
from todo_app.infrastructure.configuration.container import Application


def create_web_app(app_container: Application) -> Flask:
    """Create and configure Flask application."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"
    flask_app.config["APP_CONTAINER"] = app_container

    from . import routes

    flask_app.register_blueprint(routes.bp)

    return flask_app