from flask.testing import FlaskClient
from app.conftest import TEST_PASSWORD
from app.backend.conversations.models import Message


def test_get_message_list(client: FlaskClient, minimal_testing_setup):
    # Non-authorized login
    response = client.get('api/conversations/messages')
    assert response.status_code == 401

    # Logged-in check
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get('api/conversations/messages')
    assert response.status_code == 200
    
    assert response.get_json()['total'] == Message.query.count()


def test_get_message(client: FlaskClient, minimal_testing_setup):
    message = message = minimal_testing_setup['threads'][0].messages[0]
    message = minimal_testing_setup['threads'][0].messages[0]

    response = client.get(f'api/conversations/messages/{message.id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get(f'api/conversations/messages/{message.id}')
    assert response.status_code == 200

    assert response.get_json()['id'] == message.id

    # Non-existent message query
    response = client.get(f'api/conversations/9999')
    assert response.status_code == 404


def test_delete_message(client: FlaskClient, minimal_testing_setup):
    message = message = minimal_testing_setup['threads'][0].messages[0]

    response = client.delete(f'api/conversations/messages/{message.id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.delete(f'api/conversations/messages/{message.id}')
    assert response.status_code == 204

    # Verify that message is deleted
    response = client.get(f'api/conversations/messages/{message.id}')
    assert response.status_code == 404

