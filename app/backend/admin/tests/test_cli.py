from app import config
from app.backend.admin.сli import create_admin, remove_login_restriction
from app.app_factory import redis_client

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
    
    
def test_remove_login_restriction(runner):
    ip_address = '8.8.8.8'
    result = runner.invoke(remove_login_restriction, args=ip_address)
    assert result.exit_code == 1
    
    key = f'admin_login_attempts:{ip_address}'
    redis_client.set(key, 9999)
    
    result = runner.invoke(remove_login_restriction, args=ip_address)
    assert result.exit_code == 0
    assert redis_client.get(key) is None