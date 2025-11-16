from sqlalchemy import ForeignKey
from app.app_factory import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.backend.messages.models import Message, Thread
    from app.backend.admin.models import AdminUser, AdminNote


class Requester(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    
    ip_hash: Mapped[str] = mapped_column()
    fp_hash: Mapped[str] = mapped_column()
    
    was_approved_before: Mapped[bool] = mapped_column(default=False)
    last_reviewed_by: Mapped['AdminUser'] = relationship()
    last_reviewed_by_id: Mapped[int] = mapped_column(ForeignKey('admin_user.id'), nullable=True)
    
    messages: Mapped[List['Message']] = relationship(back_populates='requester')
    threads: Mapped[List['Thread']] = relationship(back_populates='requester')
    notes: Mapped[List['AdminNote']] = relationship(back_populates='requester')

    def __repr__(self):
        return f"<User: id={self.id}, username='{self.username}'>"