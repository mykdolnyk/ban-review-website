from flask.testing import FlaskClient
from app.conftest import TEST_PASSWORD


def test_admin_get_note_list(client: FlaskClient, minimal_testing_setup):
    response = client.get('api/admin/notes')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get('api/admin/notes')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(minimal_testing_setup['admin_notes'])
    
    # Check query params
    admin_user = minimal_testing_setup['admin_users'][0]
    response = client.get(f'api/admin/notes?author_id={admin_user.id}')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(admin_user.notes)
    assert response.get_json()['note_list'][0]['author_id'] == admin_user.id
    
    requester = minimal_testing_setup['requesters'][1]
    response = client.get(f'api/admin/notes?requester_id={requester.id}')
    assert response.status_code == 200
    assert response.get_json()['total'] == len(requester.notes)
    assert response.get_json()['note_list'][0]['requester_id'] == requester.id


def test_admin_get_note(client: FlaskClient, minimal_testing_setup):
    admin_note = minimal_testing_setup['admin_notes'][0]

    response = client.get(f'api/admin/notes/{admin_note.id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.get(f'api/admin/notes/{admin_note.id}')
    assert response.status_code == 200

    assert response.get_json()['id'] == admin_note.id

    # Non-existent note query
    response = client.get(f'api/admin/notes/9999')
    assert response.status_code == 404


def test_admin_create_note(client: FlaskClient, minimal_testing_setup):
    text = 'Testing Text'
    requester = minimal_testing_setup['requesters'][0]
    admin_user = minimal_testing_setup['admin_users'][0]

    response = client.post('/api/admin/notes', json={
        'text': text,
        'requester_id': requester.id,
        'author_id': admin_user.id
    })
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.post('/api/admin/notes', json={
        'text': text,
        'requester_id': requester.id,
        'author_id': admin_user.id
    })
    assert response.status_code == 200
    assert response.get_json()['requester_id'] == requester.id
    assert response.get_json()['author_id'] == admin_user.id


def test_admin_update_note(client: FlaskClient, minimal_testing_setup):
    new_text = 'Testing Text'
    admin_note = minimal_testing_setup['admin_notes'][0]

    response = client.put(f'/api/admin/notes/{admin_note.id}', json={
        'text': new_text,
    })
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.put(f'/api/admin/notes/{admin_note.id}', json={
        'text': new_text,
    })
    assert response.status_code == 200

    # Get the note
    response = client.get(f'api/admin/notes/{admin_note.id}')
    assert response.get_json()['text'] == new_text


def test_admin_delete_note(client: FlaskClient, minimal_testing_setup):
    admin_note = minimal_testing_setup['admin_notes'][0]

    response = client.delete(f'/api/admin/notes/{admin_note.id}')
    assert response.status_code == 401

    # Log in
    response = client.post('api/admin/login', json={
        'username': minimal_testing_setup['admin_users'][0].username,
        'password': TEST_PASSWORD
    })

    response = client.delete(f'/api/admin/notes/{admin_note.id}')
    assert response.status_code == 204

    # Get the note
    response = client.get(f'api/admin/notes/{admin_note.id}')
    assert response.status_code == 404
