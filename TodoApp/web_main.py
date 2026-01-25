from todo_app.infrastructure.configuration.container import create_application
from todo_app.infrastructure.web.app import create_web_app
from todo_app.infrastructure.notifications.factory import create_notification_service
from todo_app.interfaces.presenters.web import WebProjectPresenter, WebTaskPresenter
from todo_app.infrastructure.logging.config import configure_logging

def main():

    configure_logging(app_context="WEB")
    notification_service = create_notification_service()
    task_presenter = WebTaskPresenter()
    project_presenter = WebProjectPresenter()

    app_container = create_application(
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
        app_context="WEB",
    )
    web_app = create_web_app(app_container)
    web_app.run(debug=True)


if __name__ == "__main__":
    main()