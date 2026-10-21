"""Pemanggil kedua versi alur kerja dari sisi luar.

Berkas ini berdiri di posisi pemakai, yaitu program yang meminta sebuah alur
kerja dijalankan. Versi orkestrasi dipanggil lewat satu alamat mesin, sedangkan
versi tanpa orkestrasi dipanggil lewat layanan pertama pada rantainya. Kedua
pemanggilan memakai sesi yang sama, sehingga biaya membuka koneksi tidak
memihak salah satu versi.

Cara menjalankan: python klien.py
"""

import requests

import konfigurasi

SESI = requests.Session()

# Permintaan contoh bagi kelima alur kerja. Nominal valuta asing sengaja kecil,
# agar dua ratus putaran pengukuran tidak menghabiskan saldo nasabah.
PERMINTAAN_CONTOH = {
  "pesan-valas": {"nasabah": "N001", "mata_uang": "USD", "nominal": 10.0},
  "kirim-remitansi": {"nasabah": "N001", "mata_uang": "SGD", "nominal": 200.0},
  "bayar-tagihan": {"nasabah": "N001", "rupiah": 1250000.0},
  "tukar-poin": {"nasabah": "N002", "rupiah": 50000.0},
  "laporan-kurs": {"mata_uang": "EUR", "nominal": 1.0},
}


def jalankan_orkestrasi(nama_alur: str = "pesan-valas",
                        permintaan: dict = None):
  """Meminta mesin orkestrasi menjalankan satu alur kerja sampai selesai.

  Mengembalikan tuple berisi dict catatan proses dan int kode balasan HTTP.
  """
  isi = permintaan if permintaan is not None else PERMINTAAN_CONTOH[nama_alur]
  balasan = SESI.post(konfigurasi.alamat_alur(nama_alur), json=isi,
                      timeout=konfigurasi.BATAS_TUNGGU)
  return balasan.json(), balasan.status_code


def lanjutkan_orkestrasi(nomor: str):
  """Meminta mesin orkestrasi melanjutkan satu proses yang tertahan.

  Mengembalikan tuple berisi dict catatan proses dan int kode balasan HTTP.
  """
  alamat = (f"http://{konfigurasi.ALAMAT}:{konfigurasi.PORT_MESIN}"
            f"/lanjutkan/{nomor}")
  balasan = SESI.post(alamat, timeout=konfigurasi.BATAS_TUNGGU)
  return balasan.json(), balasan.status_code


def jalankan_berantai(permintaan: dict = None):
  """Memulai rantai layanan dengan mengirim permintaan ke layanan pertama.

  Alur kerjanya tidak disebut di sini, sebab urutannya memang tidak diketahui
  pemanggil. Mengembalikan tuple berisi dict konteks akhir dan int kode
  balasan HTTP.
  """
  isi = permintaan if permintaan is not None else dict(
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
    lompatan_orkestrasi = data.baca_pencacah()
    data.nolkan_pencacah()
    hasil_berantai, _ = jalankan_berantai()
    lompatan_berantai = data.baca_pencacah()
    print(f"Bukti versi orkestrasi : "
          f"{hasil_orkestrasi['konteks']['bukti']}")
    print(f"Bukti versi berantai   : {hasil_berantai['bukti']}")
    print(f"Lompatan orkestrasi    : {lompatan_orkestrasi}")
    print(f"Lompatan berantai      : {lompatan_berantai}")
  finally:
    kumpulan.matikan_semua()
  # Keluarannya: Lompatan orkestrasi    : 7
