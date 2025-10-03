import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os

print("Memulai proses training model...")
os.makedirs('./ml_models', exist_ok=True)

data = {
    'text': [
        'mainkan slot gacor hari ini dapatkan bonus deposit terbesar agen resmi pragmatic play',
        'link alternatif rtp live pg soft terpercaya wd cepat',
        'daftar sekarang dan menangkan jackpot maxwin slot online mudah menang',
        'situs judi bola dan casino online terbaik se-indonesia deposit pulsa',
        'selamat datang di situs berita kami, kami menyediakan informasi teknologi terkini',
        'cara memasak nasi goreng spesial resep keluarga turun temurun',
        'artikel tentang sejarah perjuangan kemerdekaan indonesia',
        'belajar pemrograman python untuk pemula dari dasar sampai mahir'
    ], 'label': ['judi', 'judi', 'judi', 'judi', 'aman', 'aman', 'aman', 'aman']
}
df = pd.DataFrame(data)
print("Dataset siap.")

model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(stop_words=None, ngram_range=(1, 2))),
    ('clf', LogisticRegression(solver='liblinear'))
])
print("Pipeline model dibuat.")

model_pipeline.fit(df['text'], df['label'])
print("Model berhasil dilatih.")

joblib.dump(model_pipeline, './ml_models/text_classifier_pipeline.joblib')
print("Pipeline model berhasil disimpan ke './ml_models/text_classifier_pipeline.joblib'")