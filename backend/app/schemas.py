from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Note(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PushSubscriptionBase(BaseModel):
    endpoint: str
    p256dh: str
    auth: str

class PushSubscriptionCreate(PushSubscriptionBase):
    pass

class PushSubscription(PushSubscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
