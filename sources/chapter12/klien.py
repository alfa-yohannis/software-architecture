"""Pemanggil kedua versi workflow dari sisi luar.

File ini berdiri di posisi pemakai, yaitu program yang meminta sebuah workflow
dijalankan. Versi orkestrasi dipanggil lewat satu alamat engine, sedangkan
versi tanpa orkestrasi dipanggil lewat layanan pertama pada rantainya. Kedua
pemanggilan memakai sesi yang sama, sehingga biaya membuka koneksi tidak
memihak salah satu versi.

Cara menjalankan: python klien.py
"""

import requests

import konfigurasi

SESI = requests.Session()

# Request contoh bagi kelima workflow. Nominal valuta asing sengaja kecil,
# agar dua ratus putaran pengukuran tidak menghabiskan saldo nasabah.
PERMINTAAN_CONTOH = {
  "pesan-valas": {"nasabah": "N001", "mata_uang": "USD", "nominal": 10.0},
  "kirim-remitansi": {"nasabah": "N001", "mata_uang": "SGD", "nominal": 200.0},
  "bayar-tagihan": {"nasabah": "N001", "rupiah": 1250000.0},
  "tukar-poin": {"nasabah": "N002", "rupiah": 50000.0},
  "laporan-kurs": {"mata_uang": "EUR", "nominal": 1.0},
}


def jalankan_orkestrasi(nama_alur: str = "pesan-valas",
                        request: dict = None):
  """Meminta orchestration engine menjalankan satu workflow sampai selesai.

  Mengembalikan tuple berisi dict catatan proses dan int kode balasan HTTP.
  """
  isi = request if request is not None else PERMINTAAN_CONTOH[nama_alur]
  balasan = SESI.post(konfigurasi.alamat_alur(nama_alur), json=isi,
                      timeout=konfigurasi.BATAS_TUNGGU)
  return balasan.json(), balasan.status_code


def lanjutkan_orkestrasi(nomor: str):
  """Meminta orchestration engine melanjutkan satu proses yang tertahan.

  Mengembalikan tuple berisi dict catatan proses dan int kode balasan HTTP.
  """
  alamat = (f"http://{konfigurasi.ALAMAT}:{konfigurasi.PORT_ENGINE}"
            f"/lanjutkan/{nomor}")
  balasan = SESI.post(alamat, timeout=konfigurasi.BATAS_TUNGGU)
  return balasan.json(), balasan.status_code


def jalankan_berantai(request: dict = None):
  """Memulai rantai layanan dengan mengirim request ke layanan pertama.

  Alur kerjanya tidak disebut di sini, sebab urutannya memang tidak diketahui
  pemanggil. Mengembalikan tuple berisi dict konteks akhir dan int kode
  balasan HTTP.
  """
  isi = request if request is not None else dict(
    PERMINTAAN_CONTOH["pesan-valas"], alur="pesan-valas")
  alamat = konfigurasi.alamat_langkah(konfigurasi.PORT_BERANTAI["nasabah"])
  balasan = SESI.post(alamat, json=isi, timeout=konfigurasi.BATAS_TUNGGU)
  return balasan.json(), balasan.status_code


if __name__ == "__main__":
  import data
  import server

  kumpulan = server.KumpulanLayanan()
  kumpulan.nyalakan_semua()
  try:
    data.setel_ulang()
    hasil_orkestrasi, _ = jalankan_orkestrasi("pesan-valas")
    hop_orkestrasi = data.baca_pencacah()
    data.nolkan_pencacah()
    hasil_berantai, _ = jalankan_berantai()
    hop_berantai = data.baca_pencacah()
    print(f"Bukti versi orkestrasi : "
          f"{hasil_orkestrasi['konteks']['bukti']}")
    print(f"Bukti versi berantai   : {hasil_berantai['bukti']}")
    print(f"Hop orkestrasi         : {hop_orkestrasi}")
    print(f"Hop berantai           : {hop_berantai}")
  finally:
    kumpulan.matikan_semua()
  # Keluarannya: Hop orkestrasi         : 7
