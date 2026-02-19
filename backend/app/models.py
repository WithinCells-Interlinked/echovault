from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Gemini embeddings are 768 or 3072 dims depending on the model
    # gemini-embedding-001 is 768 or 1024?
    # actually gemini-pro-embedding is 768.
    embedding = Column(Vector(768)) if Vector else Column(Text)

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, unique=True, index=True)
    p256dh = Column(String)
    auth = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
