"""Alamat, nomor port, dan taksonomi layanan yang dipakai seluruh Bab 12.

Berkas ini sengaja tidak memuat satu pun aturan bisnis. Isinya hanya keterangan
tempat, yaitu di port berapa sebuah layanan menunggu permintaan. Pemisahan itu
membuat skrip pengukuran dapat menyalakan dan mematikan satu layanan tanpa
menyentuh kode alur kerja maupun kode langkahnya.

Ada dua kumpulan port, sebab bab ini menjalankan dua versi yang hasilnya sama.
Kumpulan pertama dipakai versi orkestrasi, yaitu layanan pasif yang menunggu
dipanggil mesin orkestrasi. Kumpulan kedua dipakai versi tanpa orkestrasi,
yaitu layanan yang memanggil penerusnya sendiri.

Cara menjalankan: python konfigurasi.py
"""

ALAMAT = "127.0.0.1"

# Mesin orkestrasi juga menunggu di port sendiri, agar jumlah lompatan kedua
# versi dapat dibandingkan dengan cara yang sama, yaitu menghitung permintaan
# HTTP yang benar-benar dilayani.
PORT_MESIN = 7120

PORT_ORKESTRASI = {
  "nasabah": 7121,
  "kurs": 7122,
  "batas": 7123,
  "saldo": 7124,
  "transaksi": 7125,
  "bukti": 7126,
  "audit": 7127,
}

PORT_BERANTAI = {
  "nasabah": 7131,
  "kurs": 7132,
  "batas": 7133,
  "saldo": 7134,
  "transaksi": 7135,
  "bukti": 7136,
  "audit": 7137,
}

# Taksonomi layanan menurut kerangka orchestration-driven SOA. Lapisan inilah
# yang menentukan seberapa banyak alur kerja boleh memakai ulang sebuah
# layanan, dan seberapa mahal akibatnya ketika layanan itu diubah.
LAPISAN = {
  "nasabah": "enterprise",
  "kurs": "enterprise",
  "batas": "enterprise",
  "saldo": "enterprise",
  "transaksi": "enterprise",
  "bukti": "application",
  "audit": "infrastructure",
}

# Batas tunggu satu panggilan layanan. Angkanya sengaja pendek, sebab skrip
# kegagalan memang mengharapkan panggilan ke layanan yang mati gagal cepat.
BATAS_TUNGGU = 5.0


def alamat_langkah(port: int) -> str:
  """Menyusun alamat lengkap endpoint satu langkah pada port tertentu.

  Seluruh layanan memakai jalur yang sama, yaitu /langkah, sehingga pemanggil
  cukup mengetahui portnya. Mengembalikan str berisi alamat HTTP siap pakai.
  """
  return f"http://{ALAMAT}:{port}/langkah"


def alamat_alur(nama_alur: str) -> str:
  """Menyusun alamat endpoint mesin orkestrasi untuk satu nama alur kerja.

  Mengembalikan str berisi alamat HTTP yang menerima permintaan mulai alur.
  """
  return f"http://{ALAMAT}:{PORT_MESIN}/alur/{nama_alur}"


def cetak_daftar_port() -> None:
  """Mencetak seluruh port beserta lapisan layanannya ke layar.

  Dipakai saat memeriksa apakah port yang dipilih bentrok dengan program lain.
  Tidak mengembalikan nilai.
  """
  print(f"Mesin orkestrasi             : port {PORT_MESIN}")
  for nama, port in PORT_ORKESTRASI.items():
    berantai = PORT_BERANTAI.get(nama, "tidak ada")
    print(f"  {nama:<11} {LAPISAN[nama]:<15} orkestrasi {port}"
          f"  berantai {berantai}")


if __name__ == "__main__":
  cetak_daftar_port()
  # Keluarannya: Mesin orkestrasi             : port 5300
