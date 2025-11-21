from flask.testing import FlaskClient


def test_admin_login(client: FlaskClient, minimal_testing_setup):
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    admin_id = minimal_testing_setup['admin_user']['object'].id
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
        **minimal_testing_setup['admin_user']['credentials']
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
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get('api/admin/current-user')
    assert response.status_code == 200
    
    admin_id = minimal_testing_setup['admin_user']['object'].id
    assert response.get_json()['id'] == admin_id
    

def test_admin_get_user_list(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/admin/users')
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get('api/admin/users')
    assert response.status_code == 200
    assert response.get_json()['total'] == 1
    

def test_admin_get_user(client: FlaskClient, minimal_testing_setup):
    admin_id = minimal_testing_setup['admin_user']['object'].id

    response = client.get(f'api/admin/users/{admin_id}')
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.get(f'api/admin/users/{admin_id}')
    assert response.status_code == 200
    
    assert response.get_json()['id'] == admin_id
    
    # Non-existent user query
    response = client.get(f'api/admin/users/9999')
    assert response.status_code == 404
    

def test_admin_send_message_to_thread(client: FlaskClient, minimal_testing_setup):
    thread_id = minimal_testing_setup['thread'].id
    text = 'Testing Text'
    
    response = client.post(f'/api/admin/send-message/{thread_id}', json={
        'text': text
    })
    assert response.status_code == 401
    
    # Log in
    response = client.post('api/admin/login', json={
        **minimal_testing_setup['admin_user']['credentials']
    })
    
    response = client.post(f'/api/admin/send-message/{thread_id}', json={
        'text': text
    })
    assert response.status_code == 200
    assert response.get_json()['thread_id'] == thread_id