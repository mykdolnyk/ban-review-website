from flask.testing import FlaskClient

from app.backend.messages.models import Thread


def test_get_message_list(client: FlaskClient, minimal_testing_setup):
    # Non-authorized login
    response = client.get('api/messages/messages')
    assert response.status_code == 401
    
    # Logged-in check
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get('api/messages/messages')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(minimal_testing_setup['messages'])


def test_get_message(client: FlaskClient, minimal_testing_setup):
    message = minimal_testing_setup['messages'][0]
    
    response = client.get(f'api/messages/messages/{message.id}')
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get(f'api/messages/messages/{message.id}')
    assert response.status_code == 200
    
    assert response.get_json()['id'] == message.id
    
    # Non-existent message query
    response = client.get(f'api/messages/9999')
    assert response.status_code == 404


def test_delete_message(client: FlaskClient, minimal_testing_setup):
    message = minimal_testing_setup['messages'][0]
    
    response = client.delete(f'api/messages/messages/{message.id}')
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.delete(f'api/messages/messages/{message.id}')
    assert response.status_code == 204

    # Verify that message is deleted
    response = client.get(f'api/messages/messages/{message.id}')
    assert response.status_code == 404


def test_get_thread_list(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/messages/threads')
    assert response.status_code == 401
    
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get('api/messages/threads')
    assert response.status_code == 200
    assert response.get_json()['total'] == 1


def test_delete_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['thread']
    
    response = client.delete(f'api/messages/threads/{thread.id}')
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.delete(f'api/messages/threads/{thread.id}')
    assert response.status_code == 204


def test_update_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['thread']
    new_status = Thread.STATUSES.APPROVED.value
    response = client.put(f'api/messages/threads/{thread.id}', json={
        'status': new_status
    })
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.put(f'api/messages/threads/{thread.id}', json={
        'status': new_status
    })
    assert response.status_code == 200
    assert thread.status == new_status


def test_get_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['thread']
    requester = minimal_testing_setup['requester']['object']
    
    response = client.get(f'api/messages/threads/{thread.id}')
    assert response.status_code == 403
    
    # Authorize the requester
    response = client.post('/api/requesters/authenticate', json={
        'username': requester.username,
        'first_message': 'Message',
        'fp': minimal_testing_setup['requester']['credentials']['fp']
    })
    
    response = client.get(f'api/messages/threads/{thread.id}')
    assert response.status_code == 200
    assert response.get_json()['id'] == thread.id
    
    # Authorize the admin and check again
    
    with client.session_transaction() as session:
        session.clear()
    
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get(f'api/messages/threads/{thread.id}')
    assert response.status_code == 200
    assert response.get_json()['id'] == thread.id


def test_send_message_to_thread(client: FlaskClient, minimal_testing_setup):
    thread = minimal_testing_setup['thread']
    requester = minimal_testing_setup['requester']['object']
    
    response = client.post(f'api/messages/threads/{thread.id}', json={
        'text': 'Test message'
    })
    assert response.status_code == 403

    # Authorize the requester
    response = client.post('/api/requesters/authenticate', json={
        'username': requester.username,
        'first_message': 'Message',
        'fp': minimal_testing_setup['requester']['credentials']['fp']
    })
    
    response = client.post(f'api/messages/threads/{thread.id}', json={
        'text': 'Test message'
    })
    assert response.status_code == 200
    assert response.get_json()['text'] == 'Test message'
    
    # Non-existent thread query
    response = client.post(f'api/messages/threads/9999', json={
        'text': 'Test message'
    })
    assert response.status_code == 404


def test_get_thread_statuses(client: FlaskClient, minimal_testing_setup):
    statuses = {status.name: status.value for status in Thread.STATUSES}
    
    response = client.get('api/messages/threads-statuses')
    assert response.status_code == 200
    assert len(response.get_json().keys()) == len(statuses.keys())