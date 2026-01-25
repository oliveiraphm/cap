from flask import Flask
from todo_app.infrastructure.configuration.container import Application
from todo_app.infrastructure.web.middleware import trace_requests


def create_web_app(app_container: Application) -> Flask:
    
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "production" 
    flask_app.config["APP_CONTAINER"] = app_container

    trace_requests(flask_app)

    from . import routes

    flask_app.register_blueprint(routes.bp)

    return flask_app