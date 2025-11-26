from time import sleep
from flask.testing import FlaskClient
from app import config
from app.conftest import TEST_PASSWORD


def test_admin_login(client: FlaskClient, minimal_testing_setup):
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })
    admin_id = minimal_testing_setup['admin_users'][0].id
    assert response.status_code == 200
    assert response.get_json()['id'] == admin_id

    # Log out
    response = client.post('api/admin/logout')

    # Incorrect credentials login
    response = client.post('api/admin/login', json={
        'username': 'wrong-one',
        'password': 'wrong-one'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] == False


def test_admin_logout(client: FlaskClient, minimal_testing_setup):
    # Log out without prior login
    response = client.post('api/admin/logout')
    assert response.status_code == 401

    # Login
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    # Log out
    response = client.post('api/admin/logout')
    assert response.status_code == 200
    assert response.get_json()['success'] == True


def test_admin_get_current_user(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/admin/current-user')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get('api/admin/current-user')
    assert response.status_code == 200

    admin_id = minimal_testing_setup['admin_users'][0].id
    assert response.get_json()['id'] == admin_id


def test_admin_get_user_list(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/admin/users')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get('api/admin/users')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(
        minimal_testing_setup['admin_users'])


def test_admin_get_user(client: FlaskClient, minimal_testing_setup):
    admin_id = minimal_testing_setup['admin_users'][0].id

    response = client.get(f'api/admin/users/{admin_id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get(f'api/admin/users/{admin_id}')
    assert response.status_code == 200

    assert response.get_json()['id'] == admin_id

    # Non-existent user query
    response = client.get(f'api/admin/users/9999')
    assert response.status_code == 404


def test_admin_send_message_to_thread(client: FlaskClient, minimal_testing_setup):
    thread_id = minimal_testing_setup['threads'][0].id
    text = 'Testing Text'

    response = client.post(f'/api/admin/send-message/{thread_id}', json={
        'text': text
    })
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.post(f'/api/admin/send-message/{thread_id}', json={
        'text': text
    })
    assert response.status_code == 200
    assert response.get_json()['thread_id'] == thread_id


def test_limit_login_attempts(client: FlaskClient, minimal_testing_setup, monkeypatch):
    monkeypatch.setattr(config, "ADMIN_LOGIN_COOLDOWN", 3)
    
    # Reach the Login max attempts count
    for i in range(config.ADMIN_LOGIN_MAX_ATTEMPTS):
        response = client.post('api/admin/login', json={
            'username': minimal_testing_setup['admin_users'][0].username,
            'password': 'INCORRECT_PASSWORD'
        })
        assert response.status_code == 400

    # Try again with correct details but being over the limit
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })
    assert response.status_code == 429
    
    # Wait until the cooldown passes and try again with correct details
    sleep(config.ADMIN_LOGIN_COOLDOWN)

    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })
    
    assert response.status_code == 200