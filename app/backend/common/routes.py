from flask import Blueprint, abort, jsonify
from app import config
from app.backend.utils.misc import get_csrf_token


common_bp = Blueprint('common', __name__, url_prefix='/api')


@common_bp.route('/csrf-token', methods=['GET'])
def csrf_token():
    if not config.CSRF_PROTECTION:
        abort(404)

    token = get_csrf_token()
    return jsonify({"csrf_token": token})
