from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
try:
    from . import models, schemas, database, embeddings
except ImportError:
    import app.models as models
    import app.schemas as schemas
    import app.database as database
    import app.embeddings as embeddings

from fastapi.middleware.cors import CORSMiddleware
from pywebpush import webpush, WebPushException
import os
import json
import google.generativeai as genai
from sqlalchemy import text

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Create tables (SQLite in-memory or Postgres)
try:
    if os.getenv("DATABASE_URL"):
        with database.engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
except Exception as e:
    print(f"Could not enable pgvector: {e}")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="EchoVault API")

# VAPID Keys from environment
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:withincellsinterlinked@proton.me")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Must be False if allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_embedding(text: str):
    if not GEMINI_API_KEY:
        return None
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def send_push_notifications(note_title: str, db: Session):
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        return
    # ... (existing code)

def generate_and_store_embedding(note_id: int, content: str, db: Session):
    vector = embeddings.get_embedding(content)
    if vector:
        # Use raw SQL to insert into pgvector table
        from sqlalchemy import text
        db.execute(
            text("INSERT INTO note_embeddings (note_id, embedding) VALUES (:note_id, :embedding)"),
            {"note_id": note_id, "embedding": str(vector)}
        )
        db.commit()

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.1", "database": "connected" if os.getenv("DATABASE_URL") else "ephemeral"}

@app.post("/notes", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_note = models.Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    background_tasks.add_task(send_push_notifications, note.title, db)
    background_tasks.add_task(generate_and_store_embedding, db_note.id, note.content, db)
    return db_note

@app.get("/notes/search")
def search_notes(q: str, limit: int = 5, db: Session = Depends(get_db)):
    query_vector = embeddings.get_embedding(q)
    if not query_vector:
        return []
    
    from sqlalchemy import text
    # Search using cosine similarity (<=> is cosine distance in pgvector)
    # We join with notes table to get the content
    results = db.execute(
        text("""
            SELECT n.id, n.title, n.content, n.created_at, 
            (1 - (ne.embedding <=> :vector)) as similarity
            FROM notes n
            JOIN note_embeddings ne ON n.id = ne.note_id
            ORDER BY similarity DESC
            LIMIT :limit
        """),
        {"vector": str(query_vector), "limit": limit}
    ).fetchall()
    
    return [
        {
            "id": r[0], 
            "title": r[1], 
            "content": r[2], 
            "created_at": r[3],
            "similarity": float(r[4])
        } for r in results
    ]

@app.get("/notes", response_model=list[schemas.Note])
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = db.query(models.Note).offset(skip).limit(limit).all()
    return notes

@app.post("/subscriptions", response_model=schemas.PushSubscription)
def subscribe(subscription: schemas.PushSubscriptionCreate, db: Session = Depends(get_db)):
    db_sub = db.query(models.PushSubscription).filter(models.PushSubscription.endpoint == subscription.endpoint).first()
    if db_sub:
        return db_sub
    db_sub = models.PushSubscription(
        endpoint=subscription.endpoint,
        p256dh=subscription.p256dh,
        auth=subscription.auth
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@app.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.title is not None:
        db_note.title = note.title
    if note.content is not None:
        db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return {"ok": True}
