from flask_login import UserMixin
from sqlalchemy import ForeignKey
from app.app_factory import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from datetime import datetime
from app.backend.requesters.models import Requester

if TYPE_CHECKING:
    from app.backend.messages.models import Message


class AdminUser(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    messages: Mapped[List['Message']] = relationship(back_populates='admin_user')
    notes: Mapped[List['AdminNote']] = relationship(back_populates='author')
    
    @classmethod
    def active(cls):
        return db.session.query(cls).filter_by(is_active=True)

    def __repr__(self):
        return f"<User: id={self.id}, username='{self.username}'>"
    
    
class AdminNote(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    
    author_id: Mapped[int] = mapped_column(ForeignKey('admin_user.id'), nullable=True)
    author: Mapped["AdminUser"] = relationship(back_populates='notes')
    
    requester_id: Mapped[int] = mapped_column(ForeignKey('requester.id'), nullable=True)
    requester: Mapped["Requester"] = relationship(back_populates='notes')