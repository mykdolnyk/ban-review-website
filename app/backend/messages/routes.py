from flask_login import current_user
from pydantic import ValidationError
from app.backend.admin.helpers import admin_only
from app.backend.messages.models import Message, Thread
from flask import Blueprint, abort, jsonify, request, session
from app.backend.messages.schemas import MessageCreate, MessageSchema, ThreadBasicSchema, ThreadDetailedSchema
from app.app_factory import db

messages_bp = Blueprint(
    name='messages',
    import_name=__name__,
    url_prefix='/api/messages'
)


@messages_bp.route('/messages', methods=['GET'])
@admin_only
def get_message_list():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per-page', 5))
    except ValueError:
        abort(400)

    pagination = Message.query.paginate(page=page,
                                        per_page=per_page,
                                        max_per_page=25,
                                        error_out=False)

    message_list = [MessageSchema.model_validate(message).model_dump()
                    for message in pagination.items]

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "message_list": message_list
    })


@messages_bp.route('/messages/<int:id>', methods=["GET"])
@admin_only
def get_message(id: int):
    message = Message.query.filter_by(id=id).first()

    if not message:
        response = {'success': False, 'message': 'No such Message.'}
        return jsonify(response), 404

    response = MessageSchema.model_validate(message).model_dump()
    return jsonify(response)


@messages_bp.route('/messages/<int:id>', methods=["DELETE"])
@admin_only
def delete_message(id: int):
    message = Message.query.filter_by(id=id).first()

    if not message:
        response = {'success': False, 'message': 'No such Message.'}
        return jsonify(response), 404

    try:
        db.session.delete(message)
        db.session.commit()
    except Exception as e:
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    return '', 204


@messages_bp.route('/threads', methods=['GET'])
@admin_only
def get_thread_list():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per-page', 5))
    except ValueError:
        abort(400)

    pagination = Thread.active().paginate(page=page,
                                          per_page=per_page,
                                          max_per_page=25,
                                          error_out=False)

    thread_list = [ThreadBasicSchema.model_validate(thread).model_dump()
                   for thread in pagination.items]

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "thread_list": thread_list
    })


@messages_bp.route('/threads/<int:id>', methods=["GET"])
def get_thread(id: int):
    thread: Thread = Thread.active().filter_by(id=id).first()

    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404

    if thread.requester_id != session.get('requester_id') and current_user.is_anonymous:
        abort(403)

    response = ThreadDetailedSchema.model_validate(thread).model_dump()
    return jsonify(response)


@messages_bp.route('/threads/<int:id>', methods=["DELETE"])
@admin_only
def delete_thread(id: int):
    thread: Thread = Thread.active().filter_by(id=id).first()

    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404
    
    try:
        for message in thread.messages:
            db.session.delete(message)
        thread.status = Thread.STATUSES.UNRESOLVED
        db.session.commit()

    except Exception as e:
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    return '', 204


@messages_bp.route('/threads/<int:id>', methods=['POST'])
def send_message_to_thread(id: int):
    thread: Thread = Thread.active().filter_by(id=id).first()

    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404

    if thread.requester_id != session.get('requester_id'):
        abort(403)

    try:
        message_schema = MessageCreate(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    try:
        message = Message(**message_schema.model_dump(),
                          requester_id=session.get('requester_id'),
                          thread_id=thread.id)
        db.session.add(message)
        db.session.commit()

    except Exception as e:
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    response = MessageSchema.model_validate(message).model_dump()
    return jsonify(response)
