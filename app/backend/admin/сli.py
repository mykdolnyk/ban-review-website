import click
from werkzeug.security import generate_password_hash
from app.backend.admin.routes import admin_bp
from app.app_factory import db
from app.backend.admin.models import AdminUser

admin_bp.cli.help = 'Perform user-related operations.'


@admin_bp.cli.command('createsuperuser', help='Create an admin user.')
@click.argument('username')
@click.argument('email')
@click.password_option()
def createsuperuser(username, email, password):
    password_hash = generate_password_hash(password, method='scrypt:32768:8:1')

    if AdminUser.query.filter(AdminUser.username == username).first():
        click.echo('The username is already taken.')
        return False
    if AdminUser.query.filter(AdminUser.email == email).first():
        click.echo('The email is already taken.')
        return False

    user = AdminUser(username=username,
                     password=password_hash,
                     email=email,)
    db.session.add(user)
    db.session.commit()

    click.echo('The superuser has been successfully created.')
