"""Porta dan alamat yang dipakai kedua versi aplikasi Bab 11.

Kedua versi melayani request yang sama persis, sehingga hanya letak
prosesnya yang berbeda. Versi monolit menempati satu port, sedangkan versi
service-based menempati empat port, yaitu satu gateway dan tiga layanan
domain. Seluruh nomor port dikumpulkan di sini agar skrip pengukuran, skrip
kegagalan, dan skrip penjalan memakai angka yang sama.

File ini tidak dijalankan sendiri, melainkan diimpor modul lain.
"""

TUAN_RUMAH = "127.0.0.1"

PORTA_MONOLIT = 8000
PORTA_GATEWAY = 8100
PORTA_KURS = 8101
PORTA_PEMESANAN = 8102
PORTA_PENAGIHAN = 8103

# Batas tunggu satu panggilan antar proses. Nilainya sengaja pendek, sebab
# layanan yang mati harus segera ketahuan pada skrip kegagalan.
BATAS_WAKTU_DETIK = 3.0

# Satu request klien selalu memakai satu hop jaringan, baik pada versi
# monolit maupun pada versi service-based. Hop tambahan hanya muncul bila
# gateway meneruskan request itu ke layanan domain.
HOP_KLIEN = 1
HOP_LAYANAN = 1


def alamat_dasar(porta: int) -> str:
  """Menyusun alamat HTTP sebuah proses dari nomor port-nya.

  Penyusunan dikumpulkan di satu fungsi agar tuan rumahnya dapat diganti
  sekali saja, misalnya ketika layanan dipindah ke mesin lain. Mengembalikan
  str berisi alamat tanpa garis miring penutup, contohnya
  http://127.0.0.1:8101.
  """
  return f"http://{TUAN_RUMAH}:{porta}"
