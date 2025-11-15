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
    
    app = Flask(__name__)
    app.config.from_object(config_object)
    if overrides:
        app.config.update(overrides)

    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    login_manager.init_app(app=app)

    return app
