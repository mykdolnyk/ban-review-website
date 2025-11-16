from app import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.config import dictConfig as logging_config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_object=config, overrides=None):
    # logging_config(config.LOGGING)
    
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_object)
    if overrides:
        flask_app.config.update(overrides)

    db.init_app(app=flask_app)
    migrate.init_app(app=flask_app, db=db)
    login_manager.init_app(app=flask_app)
    
    from app.backend.admin.routes import admin_bp
    import app.backend.admin.сli
    flask_app.register_blueprint(admin_bp)

    return flask_app
