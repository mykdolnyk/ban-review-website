from logging import getLogger
from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_user, logout_user
from pydantic import ValidationError
from app.backend.admin.helpers import admin_only
from app.backend.admin.models import AdminNote, AdminUser
from app.backend.admin.schemas import AdminLogin, AdminNoteCreate, AdminNoteSchema, AdminNoteUpdate, AdminUserSchema
from app.app_factory import db
from app.backend.conversations.models import Message, Thread
from app.backend.conversations.schemas import MessageCreate, MessageSchema
from app.backend.utils.pagination import paginate

admin_bp = Blueprint(
    name='admin',
    import_name=__name__,
    url_prefix='/api/admin',
)

logger = getLogger(__name__)


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    if current_user.is_authenticated:
        return jsonify({
            'success': False,
            'message': 'Already logged in.'}), 400

    try:
        login_schema = AdminLogin(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    username: str = login_schema.username

    user = AdminUser.active().filter_by(username=username).first()

    login_user(user)

    response = {
        'success': True,
        'id': user.id
    }

    return jsonify(response)


@admin_bp.route('/logout', methods=['POST'])
@admin_only
def admin_logout():
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'message': 'Already logged out.'})

    logout_user()

    return jsonify({'success': True})


@admin_bp.route('/current-user', methods=['GET'])
@admin_only
def admin_get_current_user():
    user: AdminUser = current_user
    response = AdminUserSchema.model_validate(user).model_dump()
    return jsonify(response)


@admin_bp.route('/users', methods=['GET'])
@admin_only
def admin_get_user_list():
    pagination = paginate(request_args=request.args,
                          sqlalchemy_query=AdminUser.active(),
                          pydantic_model=AdminUserSchema,
                          list_name='user_list')

    return jsonify(pagination)


@admin_bp.route('/users/<int:id>', methods=["GET"])
@admin_only
def admin_get_user(id: int):
    user = AdminUser.active().filter_by(id=id).first()

    if not user:
        return {'success': False, 'message': 'No such Admin User'}, 404

    response = AdminUserSchema.model_validate(user).model_dump()
    return jsonify(response)


@admin_bp.route('/send-message/<int:id>', methods=['POST'])
@admin_only
def admin_send_message_to_thread(id: int):
    thread: Thread = Thread.active().filter_by(id=id).first()

    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404

    try:
        message_schema = MessageCreate(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    try:
        message = Message(**message_schema.model_dump(),
                          admin_user_id=current_user.id,
                          thread_id=thread.id)
        db.session.add(message)
        db.session.commit()

    except Exception as e:
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    response = MessageSchema.model_validate(message).model_dump()
    return jsonify(response)


@admin_bp.route('/notes', methods=["GET"])
@admin_only
def admin_get_note_list():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per-page', 5))
    except ValueError:
        abort(400)

    query = AdminNote.query

    # Additional query params
    author_id = request.args.get("author_id", type=int)
    if author_id is not None:
        query = query.filter(AdminNote.author_id == author_id)
    requester_id = request.args.get("requester_id", type=int)
    if requester_id is not None:
        query = query.filter(AdminNote.requester_id == requester_id)

    pagination = query.paginate(page=page,
                                per_page=per_page,
                                max_per_page=25,
                                error_out=False)

    note_list = [AdminNoteSchema.model_validate(note).model_dump()
                 for note in pagination.items]

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "note_list": note_list
    })


@admin_bp.route('/notes/<int:id>', methods=["GET"])
@admin_only
def admin_get_note(id: int):
    note = AdminNote.query.filter_by(id=id).first()

    if not note:
        response = {'success': False, 'message': 'No such Note.'}
        return jsonify(response), 404

    response = AdminNoteSchema.model_validate(note).model_dump()
    return jsonify(response)


@admin_bp.route('/notes', methods=['POST'])
@admin_only
def admin_create_note():
    try:
        note_schema = AdminNoteCreate(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    try:
        note = AdminNote(**note_schema.model_dump(), author_id=current_user.id)
        db.session.add(note)
        db.session.commit()
    except Exception as e:
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    response = AdminNoteSchema.model_validate(note).model_dump()
    return jsonify(response)


@admin_bp.route('/notes/<int:id>', methods=["DELETE"])
@admin_only
def admin_delete_note(id: int):
    note = AdminNote.query.filter_by(id=id).first()

    if not note:
        response = {'success': False, 'message': 'No such Note.'}, 404
        return jsonify(response)

    try:
        db.session.delete(note)
        db.session.commit()
    except Exception as e:
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    return '', 204


@admin_bp.route('/notes/<int:id>', methods=['PUT'])
@admin_only
def admin_update_note(id: int):
    try:
        schema = AdminNoteUpdate(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    note = AdminNote.query.filter_by(id=id).first_or_404()

    new_data = schema.model_dump(exclude_unset=True)
    for key, value in new_data.items():
        setattr(note, key, value)

    try:
        db.session.commit()
    except Exception as e:
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    response = AdminNoteSchema.model_validate(note).model_dump()

    return jsonify(response)
