import click
from sqlalchemy import func
from app import config
from app.backend.admin.helpers import generate_password_hash
from app.backend.admin.routes import admin_bp
from app.app_factory import db, redis_client
from app.backend.admin.models import AdminUser

admin_bp.cli.help = 'Perform user-related operations.'


@admin_bp.cli.command('createadmin', help='Create an admin user.')
@click.argument('username')
@click.argument('email')
@click.password_option()
def create_admin(username: str, email: str, password: str):
    password_hash = generate_password_hash(password)
    
    if AdminUser.query.filter(func.lower(AdminUser.username) == username.lower()).first():
        click.echo('The username is already taken.')
        raise click.ClickException()
    if AdminUser.query.filter(func.lower(AdminUser.email) == email.lower()).first():
        click.echo('The email is already taken.')
        raise click.ClickException()

    user = AdminUser(username=username,
                     password=password_hash,
                     email=email,)
    db.session.add(user)
    db.session.commit()

    click.echo('The admin user has been successfully created.')
    return 


@admin_bp.cli.command('removeloginrestriction', help='Remove the admin login restriction fron an IP address.')
@click.argument('ip')
def remove_login_restriction(ip: str):
    key = f'admin_login_attempts:{ip}'

    request_count = redis_client.get(key)
    if request_count is None:
        request_count = 0
    
    if int(request_count) <= config.ADMIN_LOGIN_MAX_ATTEMPTS:
        raise click.ClickException(f'The {ip} IP is not restricted.')
    else:
        redis_client.delete(key)
        click.echo(f'The restriction was lifted from the {ip} address.')