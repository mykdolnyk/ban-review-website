from flask.testing import FlaskClient
from app.app_factory import db
from app.backend.conversations.models import Message, Thread
from app.backend.requesters.models import Requester
from app.conftest import TEST_PASSWORD


def test_authenticate(client: FlaskClient):
    username = 'TestUser'
    first_message = 'This is a test message.'
    fp = 'this_is_fingerprint_string'

    # First Login
    response = client.post('/api/requesters/authenticate', json={
        'username': username,
        'first_message': first_message,
        'fp': fp
    })
    requester: Requester = Requester.query.filter_by(username=username).first()
    assert requester is not None

    thread: Thread = Thread.query.filter_by(
        requester_id=requester.id).order_by(Thread.created_on.desc()).first()
    assert thread is not None
    assert thread.id == response.get_json()['thread_id']

    message: Message = Message.query.filter_by(thread_id=thread.id).first()
    assert message is not None
    assert message.text == first_message

    assert response.status_code == 200
    with client.session_transaction() as session:
        assert session.get('requester_id') == requester.id
        # Clear the session
        session.clear()

    # Try again without the sesstion but with the same fingerprint
    response = client.post('/api/requesters/authenticate', json={
        'username': username,
        'first_message': first_message,
        'fp': fp
    })

    assert response.status_code == 200
    assert thread.id == response.get_json()['thread_id']
    with client.session_transaction() as session:
        assert session.get('requester_id') == requester.id
        # Clear the session
        session.clear()

    # Try again without the sesstion and fingerprint
    response = client.post('/api/requesters/authenticate', json={
        'username': username,
        'first_message': first_message,
        'fp': fp + 'another'
    })

    assert response.status_code == 401
    with client.session_transaction() as session:
        assert session.get('requester_id') == None
        # Clear the session
        session.clear()

    # Try again with arbitrary fingerprint but no active threads
    thread.status = Thread.STATUSES.UNRESOLVED
    db.session.commit()
    response = client.post('/api/requesters/authenticate', json={
        'username': username,
        'first_message': first_message,
        'fp': fp + 'arbitrary'
    })
    new_thread: Thread = Thread.query.filter_by(
        requester_id=requester.id).order_by(Thread.created_on.desc()).first()
    assert thread.id != new_thread.id

    assert response.status_code == 200
    assert new_thread.id == response.get_json()['thread_id']
    with client.session_transaction() as session:
        assert session.get('requester_id') == requester.id


def test_get_current_user(client: FlaskClient):
    response = client.get('/api/requesters/get-current-requester')

    assert response.status_code == 200
    assert response.get_json().get('requester') is None

    # Log in
    username = 'TestUser'
    first_message = 'This is a test message.'
    fp = 'this_is_fingerprint_string'
    response = client.post('/api/requesters/authenticate', json={
        'username': username,
        'first_message': first_message,
        'fp': fp
    })
    assert response.get_json().get('success') is True

    response = client.get('/api/requesters/get-current-requester')
    assert response.status_code == 200
    assert response.get_json().get('requester').get('username') == username


def test_get_requester_list(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/requesters/users')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get('api/requesters/users')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(minimal_testing_setup['requesters'])


def test_get_requester(client: FlaskClient, minimal_testing_setup):
    requester_id = minimal_testing_setup['requesters'][0].id

    response = client.get(f'api/requesters/users/{requester_id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get(f'api/requesters/users/{requester_id}')
    assert response.status_code == 200

    assert response.get_json()['id'] == requester_id

    # Non-existent user query
    response = client.get(f'api/requesters/users/9999')
    assert response.status_code == 404
