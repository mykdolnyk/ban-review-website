import datetime
from app.backend.conversations.helpers import create_thread
from app.backend.conversations.models import Thread
from app.backend.conversations.сli import delete_old_threads
from app.app_factory import db
from app.backend.requesters.helpers import create_requester
from app.backend.requesters.schemas import RequesterCreate

def test_delete_old_threads(runner):
    requester_schema = RequesterCreate(
        username= 'test',
        fp='test',
        first_message='test'
    )
    requester = create_requester(schema=requester_schema, testing=True)
    
    current_time = datetime.datetime.now()
    
    # Create some threads
    for day in range(30):
        thread: Thread = create_thread(
            requester=requester,
            first_message='Test'
        )
        # Change the "last_activity_on" field, the date being current date - `day`
        thread.last_activity_on = current_time - datetime.timedelta(days=day)
    db.session.commit()

    result = runner.invoke(delete_old_threads)
    assert result.exit_code == 0
    assert Thread.active().count() == 7
    # Since the default value is set to 7 days
    
    result = runner.invoke(delete_old_threads, args=['3'])
    assert result.exit_code == 0
    assert Thread.active().count() == 3