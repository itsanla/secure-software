import os
import sqlite3
import secrets
import re
import subprocess # nosec B404
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
# FIX: Gunakan variabel env untuk secret key
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))
# FIX: Matikan mode debug
app.config['DEBUG'] = False 

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg'}
UPLOAD_FOLDER = '/var/www/html/uploads/'

def koneksi_db():
    return sqlite3.connect('elearning.db')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = koneksi_db()
    cursor = conn.cursor()
    # FIX: Parameterized query untuk mencegah SQL Injection
    cursor.execute("SELECT * FROM pengguna WHERE username=?", (username,))
    pengguna = cursor.fetchone()
    
    # FIX: Gunakan check_password_hash & samarkan error (cegah User Enumeration)
    # Catatan: Asumsi kolom ke-4 (index 3) di DB adalah password hash (scrypt/pbkdf2)
    if pengguna and check_password_hash(pengguna[3], password):
        session['pengguna_id'] = pengguna[0]
        session['username'] = pengguna[1]
        session['peran'] = pengguna[4] 
        return jsonify({'pesan': 'Login berhasil', 'data': {'id': pengguna[0], 'username': pengguna[1], 'email': pengguna[2]}})
    
    # FIX: Pesan error generik
    return jsonify({'error': 'Username atau password salah'}), 401

@app.route('/materi/<int:materi_id>') # FIX: Validasi materi_id sebagai integer
def ambil_materi(materi_id):
    # FIX: Tambahkan pengecekan otorisasi sesi
    if 'pengguna_id' not in session:
        return jsonify({'error': 'Harap login terlebih dahulu'}), 403

    conn = koneksi_db()
    cursor = conn.cursor()
    # FIX: Parameterized query
    cursor.execute("SELECT * FROM materi WHERE id=?", (materi_id,))
    materi = cursor.fetchone()
    
    if materi:
        return jsonify({'judul': materi[1], 'konten': materi[2]})
    return jsonify({'error': 'Tidak ditemukan'}), 404

@app.route('/cari')
def cari_pengguna():
    kata_kunci = request.args.get('q', '')
    conn = koneksi_db()
    cursor = conn.cursor()
    # FIX: Parameterized query untuk pencarian wildcard
    cursor.execute("SELECT id, username, email FROM pengguna WHERE username LIKE ?", (f"%{kata_kunci}%",))
    hasil = cursor.fetchall()
    return jsonify({'hasil': hasil})

@app.route('/utilitas/ping')
def ping_server():
    host = request.args.get('host', 'localhost')
    # FIX: Validasi input (hanya karakter alfanumerik/IP)
    if not re.match(r"^[a-zA-Z0-9.-]+$", host):
         return jsonify({'error': 'Input host tidak valid'}), 400
         
    # FIX: Gunakan array argumen & hapus shell=True
    hasil = subprocess.run(['ping', '-c', '3', host], capture_output=True, text=True) # nosec B603 B607
    return jsonify({'output': hasil.stdout})

@app.route('/unggah', methods=['POST'])
def unggah_materi():
    # FIX: Cek otorisasi
    if 'pengguna_id' not in session:
         return jsonify({'error': 'Harap login terlebih dahulu'}), 403

    file = request.files.get('file')
    # FIX: Validasi ekstensi file & gunakan secure_filename
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        # FIX: Hapus absolute path dari response
        return jsonify({'pesan': f'File {filename} berhasil diunggah'})
    
    return jsonify({'error': 'Ekstensi file tidak diizinkan atau file kosong'}), 400

@app.route('/reset-password')
def buat_token_reset():
    email = request.args.get('email')
    # FIX: Gunakan CSPRNG yang aman & buat waktu kedaluwarsa (1 jam)
    token = secrets.token_urlsafe(32)
    expired_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    conn = koneksi_db()
    cursor = conn.cursor()
    # FIX: Parameterized query untuk INSERT & tambahkan tabel kadaluarsa
    cursor.execute("INSERT INTO token (email, token, expired_at) VALUES (?, ?, ?)", (email, token, expired_at))
    conn.commit()
    
    # FIX: Jangan ekspos token di JSON response, simulasikan kirim ke email
    return jsonify({'pesan': 'Instruksi reset telah dikirim ke email Anda'})

if __name__ == '__main__':
    # FIX: Bind ke localhost & debug dimatikan untuk keamanan
    app.run(host='127.0.0.1', port=5000, debug=False)
