import datetime
import click
from sqlalchemy import func
from app.backend.conversations.helpers import update_thread_status
from app.backend.conversations.models import Thread
from app.backend.conversations.routes import conversations_bp
from app.app_factory import db
from app.backend.admin.models import AdminUser

conversations_bp.cli.help = 'Perform conversations-related operations.'


@conversations_bp.cli.command('deleteoldthreads', help='Deletes old threads.')
@click.argument('age', required=False)
def delete_old_threads(age='7'):
    current_time = datetime.datetime.now()
    if not age:
        age = 7
    else: 
        age = int(age)
    delete_since = current_time - datetime.timedelta(days=age)

    threads = Thread.active().filter(Thread.status == Thread.STATUSES.ACTIVE,
                                     Thread.last_activity_on < delete_since)

    total_deleted = 0
    for thread in threads:
        try:
            update_thread_status(thread, Thread.STATUSES.UNRESOLVED, processed_by_system=True)
        except Exception as e:
            raise click.ClickException(f'An error ocurred when deleting the Thread {thread.id}. Total Threads deleted: {total_deleted}.')
        total_deleted += 1

    click.echo(f'The operation was completed successfully. Total Threads deleted: {total_deleted}.')
    return 