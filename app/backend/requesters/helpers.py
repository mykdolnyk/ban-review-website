import hashlib
from app.backend.requesters.models import Requester
from app.backend.requesters.schemas import RequesterSchema
from app.backend.utils.misc import get_ip_address
from app.app_factory import db


def create_requester(schema: RequesterSchema, testing=False):
    if not testing:
        ip = get_ip_address().encode()
    else: 
        ip = '8.8.8.8'.encode()
    data = {
        **schema.model_dump(exclude=['fp', 'first_message']),
        'ip_hash': hashlib.sha256(ip).hexdigest(),
    }

    requester = Requester(**data)
    db.session.add(requester)
    db.session.commit()
    
    return requester
