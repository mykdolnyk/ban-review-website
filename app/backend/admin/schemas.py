from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.backend.admin.helpers import check_password_hash
from app.backend.admin.models import AdminUser
from app.backend.requesters.models import Requester


class AdminLogin(BaseModel):
    username: str
    password: str = Field(..., max_length=128)
    
    @model_validator(mode='after')
    def check_credentials(self):
        user = AdminUser.active().filter_by(username=self.username).first()
        if not user:
            raise ValueError("Login credentials are incorrect.")

        try:
            credentials_match = check_password_hash(
                password=self.password, 
                password_hash=user.password)
        except Exception as exc:
            raise exc

        if not credentials_match:
            raise ValueError("Login credentials are incorrect.")

        return self


class AdminUserSchema(BaseModel):
    id: int
    username: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)
    
    
class AdminNoteCreate(BaseModel):
    text: str
    requester_id: int
    
    @field_validator('requester_id')
    def check_requester(requester_id: int):
        requester = Requester.query.filter_by(id=requester_id).first()
        if not requester:
            raise ValueError('Such Requester doesn\'t exist.')
        return requester_id


class AdminNoteSchema(BaseModel):
    id: int
    text: str
    created_on: datetime
    author_id: int
    requester_id: int
    
    model_config = ConfigDict(from_attributes=True)


class AdminNoteUpdate(BaseModel):
    text: str