from typing import Dict
import bcrypt
from flask.testing import FlaskClient
import pytest
from app.app_factory import create_app, db
from app.backend.admin.models import AdminNote, AdminUser
from app.backend.messages.models import Message, Thread
from app.backend.requesters.models import Requester
import config


@pytest.fixture
def app():
    overrides = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"
    }
    app = create_app(config_object=config, overrides=overrides)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def minimal_testing_setup(client: FlaskClient) -> Dict:
    """This fixture creates a `Requester` object and related to it 
    `Thread` and `Message` objects; an `AdminUser` object and related to
    it and the already existing `Thread` `Message` object."""

    # Create Requester and related Thread and Message
    requester_username = 'TestRequester'
    requester_fp = 'fingerprint_string'
    client.post('/api/requesters/authenticate', json={
        'username': requester_username,
        'first_message': 'First Message from Requester',
        'fp': requester_fp
    })
    with client.session_transaction() as session:
        session.clear()

    requester: Requester = Requester.query.filter_by(
        username=requester_username).first()
    thread = requester.threads[0]
    requester_message = thread.messages[0]

    # Create Admin and Message
    admin_username = 'TestAdmin'
    admin_password = 'test_password'

    password_hash = bcrypt.hashpw(password=admin_password.encode(),
                                  salt=bcrypt.gensalt()).decode()
    admin_user = AdminUser(username=admin_username,
                           password=password_hash,
                           email='test_email@email.com',)
    db.session.add(admin_user)
    db.session.flush()

    admin_message = Message(
        text='Second Message (by admin)',
        admin_user_id=admin_user.id,
        thread_id=thread.id
    )
    db.session.add(admin_message)
    
    admin_note = AdminNote(
        text='This is an Admin Note.',
        author_id=admin_user.id,
        requester_id=requester.id,
    )
    db.session.add(admin_note)

    db.session.commit()

    objects = {
        'requester': {
            'object': requester,
            'credentials': {
                'username': requester_username,
                'fp': requester_fp,
            }
        },
        'admin_user': {
            'object': admin_user,
            'credentials': {
                'username': admin_username,
                'password': admin_password,
            }
        },
        'admin_note': admin_note,
        'thread': thread,
        'messages': [requester_message, admin_message]
    }

    return objects
