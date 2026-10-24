from flask import Flask
from app.extensions import db, migrate, login_manager




def create_app(test_config=None):

    # initiated inside flask as outside the app package
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    ) 

    app.config.from_object("config.Config")
    if test_config is not None:
        app.config.update(test_config)

    # the actual connection betweeb database and app - migration
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    

    # login manager initialization
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "warning"



    from app.routes import main
    app.register_blueprint(main)

    from app import models

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        return response

    return app
