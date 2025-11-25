import hashlib
from uuid import uuid4
from flask import Blueprint, abort, jsonify, request, session
from pydantic import ValidationError
from app.backend.admin.helpers import admin_only
from app.backend.conversations.helpers import create_thread
from app.backend.requesters.models import Requester
from app.backend.requesters.schemas import RequesterCreate, RequesterSchema
from app.backend.conversations.models import Thread
from sqlalchemy import func
from app.app_factory import db
from app.backend.utils.misc import get_ip_address
from app.backend.requesters import helpers
from app.backend.utils.pagination import paginate

requesters_bp = Blueprint(
    name='requesters',
    import_name=__name__,
    url_prefix='/api/requesters',
)


@requesters_bp.route('/authenticate', methods=['POST'])
def authenticate_requester():
    try:
        requester_schema = RequesterCreate(**request.get_json())
    except ValidationError as error:
        return jsonify({"errors": error.errors(include_url=False, include_context=False)}), 400

    requester: Requester = Requester.query.filter(func.lower(
        Requester.username) == requester_schema.username.lower()).first()

    if not requester:
        requester = helpers.create_requester(schema=requester_schema)

    if requester.has_active_threads:
        # If the user has a session or the same fingerprint
        if session.get('requester_id') == requester.id or requester_schema.fp_hash == requester.fp_hash:
            # Log them in
            session['requester_id'] = requester.id
            thread = Thread.active().filter_by(requester_id=requester.id).first()
            response = {'success': True,
                        'message': 'Active Thread has been found.',
                        'thread_id': thread.id}

            return jsonify(response), 200
        else:
            response = {'success': False}
            return jsonify(response), 401

    else:
        # Log them in and create a new thread, update the FP and IP of the user
        ip = get_ip_address().encode()
        requester.ip_hash = hashlib.sha256(ip).hexdigest()
        requester.fp_hash = requester_schema.fp_hash

    new_thread = create_thread(requester=requester,
                               first_message=requester_schema.first_message)

    session['requester_id'] = requester.id
    response = {'success': True,
                'message': 'New Thread has been created.',
                'thread_id': new_thread.id}
    return jsonify(response), 200


@requesters_bp.route('/get-current-requester', methods=['GET'])
def get_current_requester():
    requester_id = session.get('requester_id')

    if not requester_id:
        response = {
            'requester': None
        }
    else:
        requester: Requester = Requester.query.filter_by(
            id=requester_id).first()
        active_thread = Thread.active().filter_by(requester_id=requester_id).first()
        response = {
            'requester': RequesterSchema.model_validate(requester).model_dump(),
            'thread_id': active_thread.id
        }
    return response


@requesters_bp.route('/users', methods=['GET'])
@admin_only
def get_requester_list():
    pagination = paginate(request_args=request.args,
                          sqlalchemy_query=Requester.query,
                          pydantic_model=RequesterSchema,
                          list_name='user_list')

    return jsonify(pagination)


@requesters_bp.route('/users/<int:id>', methods=["GET"])
@admin_only
def get_requester(id: int):
    user = Requester.query.filter_by(id=id).first()

    if not user:
        return {'success': False, 'message': 'No such Requester'}, 404

    response = RequesterSchema.model_validate(user).model_dump()
    return jsonify(response)
