from flask.testing import FlaskClient
from app.backend.conversations.models import Thread
from app.conftest import TEST_FP, TEST_PASSWORD


def test_get_thread_list(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/conversations/threads')
    assert response.status_code == 401

    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get('api/conversations/threads')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(
        minimal_testing_setup['threads'])

    # Locate by a thread key
    thread = minimal_testing_setup['threads'][0]
    response = client.get(f'api/conversations/threads?key={thread.key}')
    assert response.status_code == 200
    assert response.get_json()['total'] == 1
    assert response.get_json()['thread_list'][0]['id'] == thread.id

    # Locate by a requester id
    requester = minimal_testing_setup['requesters'][0]
    response = client.get(
        f'api/conversations/threads?requester_id={requester.id}')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(requester.threads)


def test_delete_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['threads'][0]

    response = client.delete(f'api/conversations/threads/{thread.id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.delete(f'api/conversations/threads/{thread.id}')
    assert response.status_code == 204


def test_update_thread(client: FlaskClient, minimal_testing_setup):
    thread: Thread = minimal_testing_setup['threads'][0]
    new_status = Thread.STATUSES.APPROVED.value
    response = client.put(f'api/conversations/threads/{thread.id}', json={
        'status': new_status
    })
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.put(f'api/conversations/threads/{thread.id}', json={
        'status': new_status
    })
    assert response.status_code == 200
    assert thread.status == new_status
    assert thread.requester.last_reviewed_by_id == minimal_testing_setup['admin_users'][0].id


def test_get_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['threads'][0]
    requester = minimal_testing_setup['requesters'][0]

    response = client.get(f'api/conversations/threads/{thread.id}')
    assert response.status_code == 403

    # Authorize the requester
    response = client.post('/api/requesters/authenticate', json={
        'username': requester.username,
        'first_message': 'Message',
        'fp': TEST_FP
    })

    response = client.get(f'api/conversations/threads/{thread.id}')
    assert response.status_code == 200
    assert response.get_json()['id'] == thread.id

    # Authorize the admin and check again

    with client.session_transaction() as session:
        session.clear()

    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get(f'api/conversations/threads/{thread.id}')
    assert response.status_code == 200
    assert response.get_json()['id'] == thread.id


def test_send_message_to_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['threads'][0]
    requester = minimal_testing_setup['requesters'][0]

    response = client.post(f'api/conversations/threads/{thread.id}', json={
        'text': 'Test message'
    })
    assert response.status_code == 403

    # Authorize the requester
    response = client.post('/api/requesters/authenticate', json={
        'username': requester.username,
        'first_message': 'Message',
        'fp': TEST_FP
    })

    response = client.post(f'api/conversations/threads/{thread.id}', json={
        'text': 'Test message'
    })
    assert response.status_code == 200
    assert response.get_json()['text'] == 'Test message'

    # Non-existent thread query
    response = client.post(f'api/conversations/threads/9999', json={
        'text': 'Test message'
    })
    assert response.status_code == 404


def test_get_thread_statuses(client: FlaskClient, minimal_testing_setup):
    statuses = {status.name: status.value for status in Thread.STATUSES}

    response = client.get('api/conversations/thread-statuses')
    assert response.status_code == 200
    assert len(response.get_json().keys()) == len(statuses.keys())
