"""Data milik setiap layanan beserta pencacah permintaan HTTP.

Setiap layanan pada bab ini hanya menyentuh satu bagian data di berkas ini.
Layanan nasabah membaca DAFTAR_NASABAH, layanan kurs membaca DAFTAR_KURS,
layanan saldo mengubah SALDO, dan seterusnya. Pemisahan itu dijaga oleh kode
langkah, bukan oleh sistem operasi, sebab seluruh layanan latihan ini berjalan
sebagai utas di dalam satu proses Python agar cukup satu perintah.

PENCACAH_PERMINTAAN dipakai untuk menghitung lompatan jaringan. Setiap layanan
yang melayani satu permintaan HTTP menambah pencacah itu satu kali, sehingga
jumlah lompatan per alur kerja dapat dihitung, bukan sekadar diperkirakan.

Kurs dasarnya mengikuti angka yang dipakai Bab 2, yaitu meniru kurs referensi
JISDOR yang diumumkan Bank Indonesia setiap hari kerja.

Cara menjalankan: python data.py
"""

import threading

# Kurs dasar dan margin per satu satuan valuta asing, dalam rupiah. Kurs dasar
# terbit untuk umum, sedangkan margin adalah keuntungan bank saat menjual.
DAFTAR_KURS = {
  "USD": {"dasar": 16250.0, "margin": 75.0},
  "EUR": {"dasar": 17600.0, "margin": 90.0},
  "SGD": {"dasar": 12100.0, "margin": 60.0},
}

DAFTAR_NASABAH = {
  "N001": {"nama": "Andi Pratama", "aktif": True, "pagu_harian": 250000000.0},
  "N002": {"nama": "Bunga Lestari", "aktif": True, "pagu_harian": 100000000.0},
  "N003": {"nama": "Candra Wijaya", "aktif": False, "pagu_harian": 50000000.0},
}

SALDO_AWAL = {
  "N001": 5000000000.0,
  "N002": 400000000.0,
  "N003": 75000000.0,
}

# Margin tambahan yang disetel skrip pemakaian ulang. Nilai nol berarti layanan
# kurs masih memakai margin aslinya.
MARGIN_TAMBAHAN = 0.0

SALDO = dict(SALDO_AWAL)
TERPAKAI_HARIAN = {}
BUKU_TRANSAKSI = []
JEJAK_AUDIT = []

PENCACAH_PERMINTAAN = 0
KUNCI = threading.Lock()


def setel_ulang() -> None:
  """Mengembalikan seluruh data yang berubah ke keadaan awalnya.

  Tanpa langkah ini, saldo nasabah habis sesudah beberapa ratus alur kerja,
  sehingga pengukuran putaran berikutnya mengukur jalur gagal, bukan jalur
  berhasil. Tidak mengembalikan nilai.
  """
  global MARGIN_TAMBAHAN
  SALDO.clear()
  SALDO.update(SALDO_AWAL)
  TERPAKAI_HARIAN.clear()
  BUKU_TRANSAKSI.clear()
  JEJAK_AUDIT.clear()
  MARGIN_TAMBAHAN = 0.0
  nolkan_pencacah()


def nolkan_pencacah() -> None:
  """Mengembalikan pencacah permintaan HTTP ke nol sebelum pengukuran baru.

  Tidak mengembalikan nilai.
  """
  global PENCACAH_PERMINTAAN
  with KUNCI:
    PENCACAH_PERMINTAAN = 0


def hitung_permintaan() -> None:
  """Menambah pencacah permintaan HTTP sebanyak satu.

  Dipanggil oleh setiap layanan dan oleh mesin orkestrasi ketika sebuah
  permintaan masuk. Kuncinya dipakai sebab server melayani permintaan pada
  utasnya sendiri. Tidak mengembalikan nilai.
  """
  global PENCACAH_PERMINTAAN
  with KUNCI:
    PENCACAH_PERMINTAAN += 1


def baca_pencacah() -> int:
  """Membaca jumlah permintaan HTTP yang sudah dilayani.

  Mengembalikan int berisi nilai pencacah saat ini.
  """
  with KUNCI:
    return PENCACAH_PERMINTAAN


def setel_margin_tambahan(tambahan: float) -> None:
  """Mengubah margin yang dipakai layanan kurs, meniru perubahan satu layanan.

  Pada sistem sungguhan langkah ini berarti memasang ulang layanan kurs. Di
  dalam latihan cukup mengubah satu angka, sebab yang diukur adalah berapa alur
  kerja yang ikut berubah hasilnya. Tidak mengembalikan nilai.
  """
  global MARGIN_TAMBAHAN
  MARGIN_TAMBAHAN = tambahan


if __name__ == "__main__":
  print(f"Nasabah terdaftar : {len(DAFTAR_NASABAH)}")
  print(f"Mata uang tersedia: {', '.join(DAFTAR_KURS)}")
  print(f"Saldo N001        : {SALDO['N001']:,.0f} rupiah")
  # Keluarannya: Saldo N001        : 5,000,000,000 rupiah
