from flask import Blueprint


users_bp = Blueprint(
    name='users',
    import_name=__name__,
    url_prefix='/api',
)

