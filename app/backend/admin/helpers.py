from functools import wraps
import bcrypt
from flask import make_response
from flask_login import current_user


def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return make_response('Unauthorized', 401)
        return function(*args, **kwargs)
    return wrapper


def generate_password_hash(password: str):
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password=password.encode(),
                                  salt=salt).decode()
    return password_hash


def check_password_hash(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())