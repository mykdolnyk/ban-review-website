from app.backend.admin.сli import create_admin


def test_create_admin(runner):
    # Create first user
    username = 'TestAdmin'
    email = 'test@email.com'
    password = 'test'
    user_input = f'{password}\n{password}\n'

    result = runner.invoke(create_admin, 
                           args=[username, email],
                           input=user_input)
    assert result.exit_code == 0
    
    # Create second user with the same name but in uppercase
    another_username = username.upper()

    result = runner.invoke(create_admin, 
                           args=[another_username, email],
                           input=user_input)
    assert result.exit_code == 1
    
    # Create second user with the same email but in uppercase
    another_email = email.upper()

    result = runner.invoke(create_admin, 
                           args=[username, another_email],
                           input=user_input)
    assert result.exit_code == 1
    
    # Create another unique user
    another_username = 'AnotherTestAdmin'
    another_email = 'anothertest@email.com'
    
    result = runner.invoke(create_admin, 
                           args=[another_username, another_email],
                           input=user_input)
    assert result.exit_code == 0