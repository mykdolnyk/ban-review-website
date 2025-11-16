from flask import Blueprint, jsonify, request
import flask_login
from pydantic import ValidationError

from app.backend.admin.models import AdminUser
from app.backend.admin.schemas import AdminLogin


admin_bp = Blueprint(
    name='admin',
    import_name=__name__,
    url_prefix='/api/admin',
)


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    if flask_login.current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': 'Already logged in.'}), 400
    
    try:
        login_schema = AdminLogin(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    username: str = login_schema.username
    
    user = AdminUser.active().filter_by(username=username).first()
    
    flask_login.login_user(user)

    response = {
        'success': True,
        'id': user.id
    }

    return jsonify(response)


@admin_bp.route('/logout', methods=['POST'])
def admin_logout():
    if flask_login.current_user.is_authenticated:
        return jsonify({
            'success': True,
            'message': 'Already logged out.'})
    
    flask_login.logout_user()

    return jsonify({'success': True})


@admin_bp.route('/current-user', methods=['GET'])
def admin_get_current_user():
    current_user: AdminUser = flask_login.current_user
    if current_user.is_anonymous:
        response = {}
        return jsonify(response)
    
    response = {
        'id': current_user.id,
        'username': current_user.username,
    }
    return jsonify(response)
