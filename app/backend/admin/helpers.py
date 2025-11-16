from functools import wraps
from flask import make_response
from flask_login import current_user


def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return make_response('Unauthorized', 401)
        return function(*args, **kwargs)
    return wrapper