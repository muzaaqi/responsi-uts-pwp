# Responsi UTS - Pemrograman Web Praktik

Panduan singkat untuk menjalankan proyek ini secara lokal dan sinkronisasi dengan repository Git (perintah PowerShell pada Windows).

## Ringkasan

Proyek ini adalah aplikasi Flask sederhana (`app.py`) yang menggunakan MySQL (via `flask_mysqldb`) dan variabel lingkungan dari file `.env`.

## Prasyarat

- Python 3.8+ terinstall
- Git terinstall dan dikonfigurasi
- MySQL server tersedia (lokal atau remote) dan kredensialnya siap

## Instalasi dan Menjalankan (Windows PowerShell)

1. Buka PowerShell di folder proyek (direktori yang berisi `app.py`).

2. Buat virtual environment dan aktifkan:

```powershell
# membuat virtualenv
python -m venv env

# aktifkan virtualenv (PowerShell)
.\env\Scripts\Activate.ps1
```

3. Pasang dependency:

```powershell
pip install -r requirements.txt
```

4. Buat file `.env` di root proyek (satu baris per variabel). Contoh `.env`:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=nama_database
```

Ganti nilai sesuai konfigurasi MySQL Anda. Pastikan database yang dipakai sudah dibuat.

5. Jalankan aplikasi:

```powershell
python app.py
```

Aplikasi akan berjalan pada http://127.0.0.1:5000/ secara default (mode debug aktif di `app.py`).

## Struktur ringkas

- `app.py` : entrypoint Flask
- `templates/` : file HTML (`index.html`, `layout.html`)
- `requirements.txt` : daftar dependency

## Git — Clone, Pull, Commit, dan Push (PowerShell)

1. Clone repository (jika belum punya salinan lokal):

```powershell
git clone https://github.com/muzaaqi/responsi-uts-pwp
cd responsi-uts-pwp
code . # Buka project di Visual Studio Code
cursor . # Buka 
```

2. Menarik (pull) perubahan dari remote ke branch aktif:

```powershell
# pastikan berada di branch yang diinginkan, mis. main
git checkout main
git pull origin main
```

3. Buat branch baru untuk fitur/perbaikan:

```powershell
git checkout -b fitur/nama-fitur
```

4. Tambah, commit, dan push perubahan:

```powershell
git add .
git commit -m "Deskripsi singkat perubahan"
git push -u origin fitur/nama-fitur
```

5. Jika hanya ingin mengirimkan update ke `main` langsung (hati-hati):

```powershell
git checkout main
git pull origin main
git merge fitur/nama-fitur   # atau rebase, tergantung workflow
git push origin main
```

Catatan keamanan: jangan pernah commit file yang berisi password atau kredensial (.env) ke repository publik. Tambahkan file `.env` ke `.gitignore` jika belum.

## Troubleshooting singkat

- Error koneksi MySQL: periksa `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, dan `MYSQL_DB` pada `.env`.
- Modul tidak ditemukan: pastikan dependency terinstall (`pip install -r requirements.txt`) dan virtualenv aktif.
- Port 5000 sudah dipakai: matikan proses yang memakai port tersebut atau ubah port di `app.run(port=xxxx)`.
