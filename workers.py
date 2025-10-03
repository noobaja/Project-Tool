import os
import time
from celery import Celery
from playwright.sync_api import sync_playwright
import joblib
import database

# --- Konfigurasi ---
BROKER_URL = "redis://localhost:6379/0"
BACKEND_URL = "redis://localhost:6379/0"

# --- Aplikasi Celery untuk Scraper ---
scraper_app = Celery('scraper_tasks', broker=BROKER_URL, backend=BACKEND_URL)

@scraper_app.task(name='tasks.scrape_url', bind=True)
def scrape_url(self, url: str):
    task_id = self.request.id
    print(f"--- [Scraper] Menerima tugas {task_id} untuk URL: {url} ---")
    page_content = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page_content = page.locator('body').inner_text()
            browser.close()
            print(f"--- [Scraper] Berhasil scraping URL: {url} ---")
    except Exception as e:
        print(f"--- [Scraper] ERROR untuk {url}: {e} ---")
        return {"url": url, "status": "Failed", "error": str(e)}

    if page_content is not None:
        print(f"--- [Scraper] Mengirim hasil dari {task_id} ke AI Worker... ---")
        scraper_app.send_task(
            'tasks.analyze_content',
            args=[{'url': url, 'content': page_content, 'task_id': task_id}],
            queue='analyze-queue'
        )
    return {"url": url, "status": "Scraping Complete"}

# --- Aplikasi Celery untuk AI Worker ---
ai_app = Celery('ai_tasks', broker=BROKER_URL, backend=BACKEND_URL)

print("--- [AI Worker] Memuat model machine learning... ---")
model_pipeline = None
try:
    model_pipeline = joblib.load('./ml_models/text_classifier_pipeline.joblib')
    print("--- [AI Worker] Model berhasil dimuat. ---")
except Exception as e:
    print(f"--- [AI Worker] KRITIS: GAGAL memuat model: {e} ---")

database.init_db()
print("--- [AI Worker] Inisialisasi DB berhasil. ---")

@ai_app.task(name='tasks.analyze_content')
def analyze_content(data: dict):
    task_id = data.get('task_id')
    url = data.get('url')
    content = data.get('content', '')
    print(f"--- [AI Worker] Menerima data untuk tugas: {task_id} ---")
    
    verdict = "Model Error"
    if model_pipeline:
        try:
            prediction = model_pipeline.predict([content])
            verdict = prediction[0]
            print(f"--- [AI Worker] PREDIKSI MODEL untuk {task_id}: '{verdict.upper()}' ---")
        except Exception as e:
            print(f"--- [AI Worker] GAGAL prediksi: {e} ---")
    
    db = database.SessionLocal()
    try:
        db_result = db.query(database.AnalysisResult).filter(database.AnalysisResult.task_id == task_id).first()
        if db_result:
            db_result.is_suspicious = True if verdict == 'judi' else False
            db_result.verdict = verdict
            db_result.status = "COMPLETE"
            db.commit()
            print(f"--- [AI Worker] Hasil untuk {task_id} berhasil diupdate di DB. ---")
    except Exception as e:
        db.rollback()
        print(f"--- [AI Worker] GAGAL menyimpan ke DB: {e} ---")
    finally:
        db.close()
    return {"url": url, "verdict": verdict}