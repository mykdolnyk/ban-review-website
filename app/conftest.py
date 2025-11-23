from typing import Dict
from flask.testing import FlaskClient
import pytest
from app.app_factory import create_app, db
from app.backend.admin.helpers import generate_password_hash
from app.backend.admin.models import AdminNote, AdminUser
from app.backend.conversations.helpers import create_thread
from app.backend.conversations.models import Message, Thread
from app.backend.requesters.helpers import create_requester
from app.backend.requesters.models import Requester
from app.backend.requesters.schemas import RequesterCreate
import config

TEST_FP = 'testing-fingerprint'
TEST_PASSWORD = 'testing-password'


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

    objects = {
        'requesters': [],
        'threads': [],
        'admin_users': [],
        'admin_notes': []
    }

    # Create Requester and related Thread and Message
    for i in range(2):
        requester_schema = RequesterCreate(
            username=f'Requester{i}',
            fp=TEST_FP,
            first_message=f'This is first message. Index: {i}'
        )
        requester = create_requester(schema=requester_schema, testing=True)
        objects['requesters'].append(requester)

        create_thread(requester=requester,
                      first_message=requester_schema.first_message)
        objects['threads'].extend(requester.threads)

    # Create Admin, Message, Note
    password_hash = generate_password_hash(TEST_PASSWORD)
    for j in range(2):
        admin_user = AdminUser(username=f'TestAdmin{j}',
                               password=password_hash,
                               email=f'test_email{j}@email.com')
        db.session.add(admin_user)
        db.session.flush()

        # Create a Message
        admin_message = Message(
            text='Second Message (by admin)',
            admin_user_id=admin_user.id,
            thread_id=objects['threads'][j].id
            # ^ send a message to the thread corresponding to the admin's id
        )
        db.session.add(admin_message)
        objects['admin_users'].append(admin_user)

        # Create a Note
        admin_note = AdminNote(
            text='This is an Admin Note.',
            author_id=admin_user.id,
            requester_id=objects['requesters'][j].id,
            # ^ create a note for the requester corresponding to the admin's id
        )
        db.session.add(admin_note)
        objects['admin_notes'].append(admin_note)

    db.session.commit()

    return objects
