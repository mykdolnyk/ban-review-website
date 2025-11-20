from uuid import uuid4
from flask import Blueprint, jsonify, request, session
from pydantic import ValidationError
from app.backend.requesters.models import Requester
from app.backend.requesters.schemas import RequesterCreate, RequesterSchema
from app.backend.messages.models import Message, Thread
from sqlalchemy import func
from app.app_factory import db
from app.utils.misc import get_ip_address
import hashlib

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
        # Create one
        ip = get_ip_address().encode()
        data = {
            **requester_schema.model_dump(exclude=['fp', 'first_message']),
            'ip_hash': hashlib.sha256(ip).hexdigest(),
        }

        requester = Requester(**data)
        db.session.add(requester)

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

    new_thread = Thread(
        key=str(uuid4()),
        requester_id=requester.id
    )
    db.session.add(new_thread)
    db.session.flush()
    new_message = Message(
        text=requester_schema.first_message,
        requester_id=requester.id,
        thread_id=new_thread.id,
    )
    db.session.add(new_message)
    db.session.commit()

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
        requester: Requester = Requester.query.filter_by(id=requester_id).first()
        active_thread = Thread.active().filter_by(requester_id=requester_id).first()
        response = {
            'requester': RequesterSchema.model_validate(requester).model_dump(),
            'thread_id': active_thread.id
        }
    return response