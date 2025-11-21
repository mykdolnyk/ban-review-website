from app.backend.messages.models import Thread
from app.app_factory import db


def update_thread_status(thread: Thread, new_status: Thread.STATUSES, no_deletion=False):
    if new_status == Thread.STATUSES.ACTIVE:
        thread.status = Thread.STATUSES.ACTIVE
        db.session.commit()
        return True

    # The 'finished' statuses
    if new_status == Thread.STATUSES.APPROVED:
        thread.status = Thread.STATUSES.APPROVED
        approved_hooks(thread)
        
    elif new_status == Thread.STATUSES.DENIED:
        thread.status = Thread.STATUSES.DENIED
        denied_hooks(thread)

    elif new_status == Thread.STATUSES.UNRESOLVED:
        thread.status = Thread.STATUSES.UNRESOLVED
        unresolved_hooks(thread)

    else:
        raise ValueError('No such status.')
    
    # Delete the conversation
    if not no_deletion:
        for message in thread.messages:
            db.session.delete(message)
        
    db.session.commit()
    return True


def approved_hooks(thread: Thread):
    return None


def denied_hooks(thread: Thread):
    return None


def unresolved_hooks(thread: Thread):
    return None