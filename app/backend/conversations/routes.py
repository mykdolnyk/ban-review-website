from logging import getLogger
from flask_login import current_user
from pydantic import ValidationError
from app.backend.admin.helpers import admin_only
from app.backend.conversations.helpers import generate_thread_key, update_thread_status
from app.backend.conversations.models import Message, Thread
from flask import Blueprint, abort, jsonify, request, session
from app.backend.conversations.schemas import MessageCreate, MessageSchema, ThreadBasicSchema, ThreadDetailedSchema, ThreadUpdate
from app.app_factory import db
from app.utils.pagination import paginate

conversations_bp = Blueprint(
    name='messages',
    import_name=__name__,
    url_prefix='/api/conversations'
)

logger = getLogger(__name__)


@conversations_bp.route('/messages', methods=['GET'])
@admin_only
def get_message_list():
    pagination = paginate(request_args=request.args,
                          sqlalchemy_query=Message.query,
                          pydantic_model=MessageSchema,
                          list_name='message_list')

    return jsonify(pagination)


@conversations_bp.route('/messages/<int:id>', methods=["GET"])
@admin_only
def get_message(id: int):
    message = Message.query.filter_by(id=id).first()

    if not message:
        response = {'success': False, 'message': 'No such Message.'}
        return jsonify(response), 404

    response = MessageSchema.model_validate(message).model_dump()
    return jsonify(response)


@conversations_bp.route('/messages/<int:id>', methods=["DELETE"])
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
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    return '', 204


@conversations_bp.route('/threads', methods=['GET'])
@admin_only
def get_thread_list():
    query = Thread.query
    
    # query params
    thread_key = request.args.get("key", type=str)
    if thread_key is not None:
        query = query.filter(Thread.key == thread_key)
    
    requester_id = request.args.get("requester_id", type=int)
    if requester_id is not None:
        query = query.filter(Thread.requester_id == requester_id)
    
    
    pagination = paginate(request_args=request.args,
                          sqlalchemy_query=query,
                          pydantic_model=ThreadBasicSchema,
                          list_name='thread_list')

    return jsonify(pagination)


@conversations_bp.route('/threads/<int:id>', methods=["DELETE"])
@admin_only
def delete_thread(id: int):
    thread: Thread = Thread.active().filter_by(id=id).first()

    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404
    
    try:
        update_thread_status(
            thread=thread,
            new_status=Thread.STATUSES.UNRESOLVED
        )

    except Exception as e:
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    return '', 204


@conversations_bp.route('/threads/<int:id>', methods=['PUT'])
@admin_only
def update_thread(id: int):
    try:
        schema = ThreadUpdate(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    thread: Thread = Thread.active().filter_by(id=id).first()
    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404
    
    try:
        update_thread_status(
            thread=thread,
            new_status=schema.status
        )

    except Exception as e:
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500    

    response = ThreadDetailedSchema.model_validate(thread).model_dump()
    return jsonify(response)


@conversations_bp.route('/threads/<int:id>', methods=["GET"])
def get_thread(id: int):
    thread: Thread = Thread.active().filter_by(id=id).first()

    if not thread:
        response = {'success': False, 'message': 'No such Thread.'}
        return jsonify(response), 404

    if thread.requester_id != session.get('requester_id') and current_user.is_anonymous:
        abort(403)

    response = ThreadDetailedSchema.model_validate(thread).model_dump()
    return jsonify(response)


@conversations_bp.route('/threads/<int:id>', methods=['POST'])
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
        logger.exception(e)
        return {'success': False,
                'message': 'Unknown error occured'}, 500

    response = MessageSchema.model_validate(message).model_dump()
    return jsonify(response)


@conversations_bp.route('/thread-statuses', methods=['GET'])
def get_thread_statuses():
    statuses = {status.name: status.value for status in Thread.STATUSES}
    
    return jsonify(statuses)