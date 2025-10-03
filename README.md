# 🛡️ GuardianWeb - AI-Powered URL Analyzer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green?style=for-the-badge&logo=fastapi)
![Celery](https://img.shields.io/badge/Celery-5.x-orange?style=for-the-badge&logo=celery)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-blueviolet?style=for-the-badge&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge)

GuardianWeb adalah sebuah platform analisis URL berbasis AI yang dirancang untuk mendeteksi situs web berbahaya seperti phishing dan judi online. Sistem ini menggunakan arsitektur asinkron untuk melakukan analisis mendalam tanpa mengorbankan kecepatan respons.

## ✨ Fitur Utama
- **Analisis Asinkron**: Pengguna mendapatkan ID tugas secara instan sementara analisis berat berjalan di latar belakang.
- **Deteksi Multi-Lapis**: Menggabungkan beberapa teknik, termasuk analisis konten berbasis Machine Learning (klasifikasi teks).
- **Arsitektur Berbasis Worker**: Menggunakan Celery untuk mendistribusikan tugas scraping dan analisis AI secara efisien.
- **Antarmuka Web Sederhana**: UI yang bersih dan intuitif untuk memasukkan URL dan melihat hasilnya.
- **API yang Jelas**: Menyediakan endpoint RESTful untuk mengirim URL dan mengambil hasil analisis.

## 🏗️ Arsitektur
Aplikasi ini berjalan sebagai serangkaian proses Python yang saling berkomunikasi menggunakan task queue (Redis).

**Alur Kerja:**
`Frontend` -> `API (FastAPI)` -> `Redis` -> `Scraper Worker` -> `Redis` -> `AI Worker` -> `PostgreSQL`

- **Frontend**: Halaman web statis (HTML, CSS, JS) yang berfungsi sebagai antarmuka pengguna.
- **Backend**:
    - **API Server (`main.py`)**: Dibangun dengan FastAPI, bertindak sebagai pintu gerbang untuk semua permintaan.
    - **Task Queue (`workers.py`)**: Dikelola oleh Celery dengan Redis sebagai *broker*.
    - **Scraper Worker**: Bertugas mengunjungi URL menggunakan Playwright dan mengekstrak konten teksnya.
    - **AI Worker**: Menerima teks, menjalankan model klasifikasi (Scikit-learn) untuk prediksi, dan menyimpan hasilnya.
- **Database (PostgreSQL)**: Menyimpan semua hasil analisis secara permanen.

## 🚀 Tumpukan Teknologi
- **Backend**: Python, FastAPI, Celery, SQLAlchemy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Machine Learning**: Scikit-learn, Pandas, Joblib
- **Web Scraping**: Playwright
- **Database & Broker**: PostgreSQL, Redis
- **Server**: Uvicorn

## 🛠️ Instalasi & Persiapan

Pastikan Anda memiliki prasyarat berikut terinstal di sistem WSL/Linux Anda.

**Prasyarat:**
- Python 3.9+
- Redis Server
- PostgreSQL Server
- Git

**Langkah-langkah Persiapan:**
1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/nama-anda/guardian-web-analyzer.git](https://github.com/nama-anda/guardian-web-analyzer.git)
    cd guardian-web-analyzer
    ```
2.  **Buat dan aktifkan Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Instal semua dependensi Python:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Instal browser untuk Playwright:**
    ```bash
    playwright install --with-deps
    ```
5.  **Siapkan Database PostgreSQL:**
    - Pastikan service PostgreSQL berjalan.
    - Buat user dan database sesuai dengan konfigurasi di bawah ini (atau sesuaikan dengan `.env`):
      ```sql
      CREATE DATABASE guardian_db;
      CREATE USER guardian WITH PASSWORD 'secret';
      ALTER DATABASE guardian_db OWNER TO guardian;
      ```
6.  **Konfigurasi Environment**:
    - Buat file `.env` dari `env.example` (jika ada) atau buat baru.
    - Isi file `.env` dengan kredensial database Anda.
7.  **Latih Model Awal**:
    - Jalankan skrip training untuk menghasilkan file model pertama.
      ```bash
      python train_model.py
      ```

## ▶️ Cara Menjalankan
Aplikasi ini membutuhkan 3-4 terminal terpisah untuk berjalan. Pastikan Anda sudah mengaktifkan `venv` (`source .venv/bin/activate`) di setiap terminal.

1.  **Terminal 1 - Jalankan API Server:**
    ```bash
    uvicorn main:app --reload
    ```
2.  **Terminal 2 - Jalankan Scraper Worker:**
    ```bash
    celery -A workers:scraper_app worker -l info -Q scrape-queue
    ```
3.  **Terminal 3 - Jalankan AI Worker:**
    ```bash
    celery -A workers:ai_app worker -l info -Q analyze-queue
    ```
4.  **(Opsional) Terminal 4 - Jalankan Frontend:**
    ```bash
    # Navigasi ke folder frontend
    cd ../frontend
    python -m http.server 8001
    ```
- Akses API di `http://localhost:8000/docs`.
- Akses Frontend di `http://localhost:8001`.

## 📖 Endpoint API

### `POST /analyze`
Mengirimkan URL baru untuk dianalisis.
- **Query Parameter**: `url` (string, wajib).
- **Respons Sukses (202 Accepted)**:
  ```json
  {
    "message": "Analysis task received",
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }