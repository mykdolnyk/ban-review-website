from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MessageSchema(BaseModel):
    id: int
    text: str
    created_on: datetime
    thread_id: int
    admin_user_id: Optional[int]
    requester_id: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    text: str


class ThreadBasicSchema(BaseModel):
    id: int
    status: int
    created_on: datetime
    last_activity_on: datetime
    requester_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ThreadDetailedSchema(BaseModel):
    id: int
    status: int
    created_on: datetime
    last_activity_on: datetime
    requester_id: int
    messages: List[MessageSchema]
    
    model_config = ConfigDict(from_attributes=True)
    
