from app import config
from flask import Flask, abort, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.config import dictConfig as logging_config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_object=config, overrides=None):
    logging_config(config.LOGGING)
    
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_object)
    if overrides:
        flask_app.config.update(overrides)

    db.init_app(app=flask_app)
    migrate.init_app(app=flask_app, db=db)
    login_manager.init_app(app=flask_app)
    
    from app.backend.admin.models import AdminUser
    @login_manager.user_loader
    def user_loader(user_id: str):
        return AdminUser.query.get(int(user_id))
    
    from app.backend.admin.routes import admin_bp
    from app.backend.requesters.routes import requesters_bp
    from app.backend.conversations.routes import conversations_bp
    from app.backend.common.routes import common_bp
    import app.backend.admin.сli
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(requesters_bp)
    flask_app.register_blueprint(conversations_bp)
    flask_app.register_blueprint(common_bp)

    @flask_app.before_request
    def csrf_protect():
        if flask_app.config.get('TESTING') or not flask_app.config.get('CSRF_PROTECTION'):
            return None
        
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            header_token = request.headers.get('X-CSRF-Token')
            session_token = session.get('csrf_token')
            if not header_token or not session_token or header_token != session_token:
                abort(403, 'CSRF token is missing or is invalid.')

    return flask_app
