from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey
from app.app_factory import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.users.models import Requester

if TYPE_CHECKING:
    from app.backend.admin.models import AdminUser


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    
    admin_user_id: Mapped[int] = mapped_column(ForeignKey('admin_user.id'), nullable=True)
    admin_user: Mapped["AdminUser"] = relationship(back_populates='messages')
    
    requester_id: Mapped[int] = mapped_column(ForeignKey('requester.id'), nullable=True)
    requester: Mapped["Requester"] = relationship(back_populates='messages')
    
    thread_id: Mapped[int] = mapped_column(ForeignKey('thread.id'))
    thread: Mapped['Thread'] = relationship(back_populates='messages')


class Thread(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column()
    
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    last_activity_on: Mapped[datetime] = mapped_column(onupdate=datetime.now)
    
    messages: Mapped[List["Message"]] = relationship(back_populates='thread')
    
    requester_id: Mapped[int] = mapped_column(ForeignKey('requester.id'))
    requester: Mapped["Requester"] = relationship(back_populates='threads')
