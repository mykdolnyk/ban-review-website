from functools import wraps
import bcrypt
from flask import abort, make_response
from flask_login import current_user
from app.backend.utils.misc import get_ip_address
from app.app_factory import redis_client
from app import config


def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return make_response('Unauthorized', 401)
        return function(*args, **kwargs)
    return wrapper


def limit_login_attempts(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        ip = get_ip_address()
        key = f'admin_login_attempts:{ip}'

        request_count = redis_client.incr(key)

        if request_count == 1:
            redis_client.expire(key, config.ADMIN_LOGIN_COOLDOWN)
        elif request_count > config.ADMIN_LOGIN_MAX_ATTEMPTS:
            abort(429)
        return function(*args, **kwargs)

    return wrapper


def generate_password_hash(password: str):
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password=password.encode(),
                                  salt=salt).decode()
    return password_hash


def check_password_hash(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
