import re

class ValidasiError(Exception):
    """Exception kustom untuk menangani kesalahan validasi input."""
    pass

def validasi_email(email: str) -> str:
    """Validasi format email dengan batasan panjang dan karakter."""
    if not isinstance(email, str):
        raise ValidasiError('Email harus berupa teks.')
    
    email = email.strip().lower()
    
    if not email:
        raise ValidasiError('Email tidak boleh kosong.')
    if len(email) > 254:
        raise ValidasiError('Email terlalu panjang.')
        
    # Regex untuk memastikan format email standar dan menghindari karakter berbahaya
    pola = r'^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$'
    if not re.match(pola, email):
        raise ValidasiError('Format email tidak valid.')
        
    return email

def validasi_nim(nim: str) -> str:
    """Validasi NIM agar sesuai dengan standar 10 digit angka."""
    if not isinstance(nim, str):
        raise ValidasiError('NIM harus berupa teks.')
        
    nim = nim.strip()
    if not re.match(r'^\d{10}$', nim):
        raise ValidasiError('NIM harus tepat 10 digit angka.')
        
    return nim

def validasi_nilai(nilai) -> float:
    """Validasi skor angka agar berada dalam rentang 0.0 - 100.0."""
    try:
        nilai_float = float(nilai)
    except (TypeError, ValueError):
        raise ValidasiError('Nilai harus berupa angka.')

    if not (0.0 <= nilai_float <= 100.0):
        raise ValidasiError('Nilai harus berada di rentang 0 hingga 100.')
        
    return nilai_float

# ─── PROSEDUR PENGUJIAN ──────────────────────────────────────────

def jalankan_tes():
    kasus_uji = [
        ('Email Valid', validasi_email, 'mahasiswa@pnp.ac.id'),
        ('Email Invalid', validasi_email, 'bukan_email'),
        ('Injeksi SQL (Email)', validasi_email, "' OR '1'='1"),
        ('NIM Valid', validasi_nim, '2021234567'),
        ('NIM Karakter Non-Angka', validasi_nim, '202ABCD567'),
        ('Nilai Valid', validasi_nilai, 85.5),
        ('Nilai Negatif', validasi_nilai, -10),
        ('Injeksi SQL (Nilai)', validasi_nilai, '1; DROP TABLE--'),
    ]

    print(f"{'STATUS':<10} | {'SKENARIO':<25} | {'HASIL / PESAN ERROR'}")
    print("-" * 70)

    for label, fungsi, data in kasus_uji:
        try:
            hasil = fungsi(data)
            print(f"{'✅ OK':<10} | {label:<25} | {repr(hasil)}")
        except ValidasiError as e:
            print(f"{'❌ REJECT':<10} | {label:<25} | {e}")

if __name__ == '__main__':
    jalankan_tes()