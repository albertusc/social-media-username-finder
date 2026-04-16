# Social Media Comment Username Scraper

Aplikasi Flask untuk mencari username tertentu pada komentar/reply di beberapa platform:
- Instagram
- Facebook
- YouTube
- TikTok
- X (Twitter)

Setiap platform memiliki halaman input sendiri, lalu hasil pencarian ditampilkan pada halaman result beserta screenshot ketika username ditemukan.

## Fitur Utama

- UI yang konsisten, ringan, dan responsif (desktop/mobile).
- Halaman form per platform dengan validasi input dasar.
- Hasil scraping dalam satu halaman result dengan status Found/Not Found.
- Preview screenshot dalam modal dengan zoom + pan.
- Struktur Flask modular menggunakan blueprint per platform.

## Struktur Project

- app.py: Entry point aplikasi Flask dan routing utama.
- instagram.py: Logic scraping Instagram.
- facebook.py: Logic scraping Facebook.
- youtube.py: Logic scraping YouTube.
- tiktok.py: Logic scraping TikTok.
- x.py: Logic scraping X (Twitter).
- templates/: Seluruh halaman HTML.
- static/: File statis (CSS dan screenshot hasil scraping).
- chromedriver-win64/: Binary chromedriver lokal (opsional untuk disimpan di repo).

## Prasyarat

- Python 3.10+ (disarankan)
- Google Chrome terpasang
- Koneksi internet stabil
- Windows (project saat ini disiapkan dan diuji di Windows)

## Instalasi

1. Clone atau buka folder project ini.
2. Buat virtual environment:

```powershell
python -m venv .venv
```

3. Aktifkan virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Install dependency:

```powershell
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```powershell
python app.py
```

Aplikasi berjalan di:
- http://127.0.0.1:5000

## Alur Pakai

1. Buka halaman Home.
2. Pilih platform.
3. Isi form (URL konten + username target, dan kredensial jika dibutuhkan).
4. Klik Start Scraping.
5. Lihat hasil di halaman result.

## Catatan Penting

- Beberapa platform membutuhkan login dan bisa berubah UI sewaktu-waktu, sehingga selector Selenium mungkin perlu update.
- Project ini menyimpan screenshot hasil ke folder static/.
- Jangan commit data sensitif (email/password) ke repository.

## Upload ke GitHub

Project ini sudah disiapkan dengan .gitignore agar file yang tidak perlu tidak ikut terupload (cache Python, virtual env, screenshot sementara, dll).

Langkah singkat:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <URL_REPO_GITHUB>
git push -u origin main
```

## Troubleshooting Singkat

- Jika browser/driver gagal jalan:
  - Pastikan versi Chrome kompatibel.
  - Coba update package:

```powershell
pip install -U selenium undetected-chromedriver
```

- Jika halaman target berubah layout:
  - Perlu penyesuaian locator Selenium pada file platform terkait.

## Disclaimer

Gunakan untuk kebutuhan testing/analisis yang legal dan sesuai Terms of Service platform terkait.
