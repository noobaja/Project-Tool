import os
import time
from celery import Celery
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from fastapi.middleware.cors import CORSMiddleware
import schemas
import database

# --- Konfigurasi Aplikasi ---
app = FastAPI(title="GuardianWeb API")
celery_sender = Celery('sender', broker="redis://localhost:6379/0")

# --- Konfigurasi CORS ---
origins = ["http://localhost", "http://localhost:8001", "http://127.0.0.1:8001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("API Gateway memulai, mencoba koneksi ke DB...")
    retries = 5
    delay = 3
    for i in range(retries):
        try:
            database.init_db()
            print("Koneksi DB & inisialisasi tabel berhasil.")
            break
        except OperationalError:
            print(f"DB belum siap, mencoba lagi dalam {delay} detik...")
            time.sleep(delay)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoint API ---
@app.post("/analyze", status_code=202)
def analyze_url(url: str, db: Session = Depends(get_db)):
    task = celery_sender.send_task('tasks.scrape_url', args=[url], queue='scrape-queue')
    initial_entry = database.AnalysisResult(task_id=task.id, url=url, status="PENDING")
    db.add(initial_entry)
    db.commit()
    return {"message": "Analysis task received", "task_id": task.id}

@app.post("/results")
def get_results(request_data: schemas.TaskIdList, db: Session = Depends(get_db)):
    results = db.query(database.AnalysisResult).filter(
        database.AnalysisResult.task_id.in_(request_data.task_ids)
    ).all()
    if not results:
        return {"message": "No results found."}
    return results

@app.get("/")
def read_root():
    return {"message": "Welcome to GuardianWeb API"}