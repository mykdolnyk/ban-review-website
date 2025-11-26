from fakeredis import FakeRedis
from redis import Redis
from app import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_redis import FlaskRedis
from logging.config import dictConfig as logging_config
from app.backend.utils.misc import setup_csrf
from app.backend.utils.rate_limiting import setup_rate_limiting


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
redis_client: Redis = FlaskRedis()


def create_app(config_object=config, overrides=None):
    logging_config(config.LOGGING)
    
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_object)
    flask_app.debug = True
    if overrides:
        flask_app.config.update(overrides)

    db.init_app(app=flask_app)
    migrate.init_app(app=flask_app, db=db)
    login_manager.init_app(app=flask_app)
    redis_client.init_app(app=flask_app)
    if flask_app.testing:
        redis_client._redis_client = FakeRedis()

    from app.backend.admin.models import AdminUser
    @login_manager.user_loader
    def user_loader(user_id: str):
        return AdminUser.query.get(int(user_id))
    
    from app.backend.admin.routes import admin_bp
    from app.backend.requesters.routes import requesters_bp
    from app.backend.conversations.routes import conversations_bp
    from app.backend.common.routes import common_bp
    import app.backend.admin.сli
    import app.backend.conversations.сli
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(requesters_bp)
    flask_app.register_blueprint(conversations_bp)
    flask_app.register_blueprint(common_bp)

    setup_csrf(app=flask_app)
    setup_rate_limiting(app=flask_app, redis_client=redis_client)
    
    return flask_app
