from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from . import models, schemas, database
from fastapi.middleware.cors import CORSMiddleware
from pywebpush import webpush, WebPushException
import os
import json

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="EchoVault API")

# VAPID Keys from environment
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:withincellsinterlinked@proton.me")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_push_notifications(note_title: str, db: Session):
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        return

    subscriptions = db.query(models.PushSubscription).all()
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth
                    }
                },
                data=json.dumps({
                    "title": "New Note in EchoVault",
                    "body": note_title
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL}
            )
        except WebPushException as ex:
            print("WebPush error: {}", ex)
            if ex.response and ex.response.status_code == 410:
                # Subscription has expired or is no longer valid
                db.delete(sub)
                db.commit()

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/notes", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_note = models.Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Send push notifications in background
    background_tasks.add_task(send_push_notifications, note.title, db)
    
    return db_note

@app.get("/notes", response_model=list[schemas.Note])
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = db.query(models.Note).offset(skip).limit(limit).all()
    return notes

@app.post("/subscriptions", response_model=schemas.PushSubscription)
def subscribe(subscription: schemas.PushSubscriptionCreate, db: Session = Depends(get_db)):
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