"""Aturan konversi mata uang beserta bentuk tugas yang dikerjakan processing unit.

Berkas ini tidak mengenal tuple space, proses, maupun basis data. Isinya hanya
tabel kurs awal, satu fungsi hitung, dan kelas Tugas. Karena itu aturan yang sama
dapat dipakai processing unit, skrip pengukuran, dan pengujian tanpa menyalakan
satu proses pun.

Nilai kurs meniru kurs referensi yang diterbitkan Bank Indonesia setiap hari
kerja. Nilai itu jarang berubah dalam sehari, sehingga layak disalin ke memori
setiap processing unit.

Cara menjalankan: python domain.py
"""

import dataclasses

# Kurs awal yang diisikan ke basis data. Processing unit tidak membaca tabel ini
# langsung, melainkan membaca salinannya di grid memori masing-masing.
KURS = {
  ("USD", "IDR"): 16250.0,
  ("EUR", "IDR"): 17600.0,
  ("SGD", "IDR"): 12100.0,
}

# Nomor versi kurs yang pertama kali diterbitkan. Angka ini naik setiap kali
# pembaru kurs menerbitkan nilai baru, sehingga pembaca dapat mengetahui bahwa
# salinan di grid memorinya sudah tertinggal.
VERSI_AWAL = 1

# Banyaknya baris transaksi di dalam satu tugas. Satu tugas meniru satu berkas
# setoran, bukan satu permintaan tunggal, sebab satu perkalian saja terlalu
# ringan untuk dibandingkan dengan biaya menyimpan hasilnya. Angka ini dipilih
# agar menghitung satu tugas memakan waktu sekitar satu milidetik.
TRANSAKSI_PER_TUGAS = 3000

# Nominal setiap transaksi dibentuk dari nomor tugas dan urutannya, agar hasil
# yang sama dapat dihitung ulang tanpa menyimpan daftar transaksinya.
NOMINAL_TERKECIL = 10
RENTANG_NOMINAL = 991
PENGALI_NOMOR = 7
PENGALI_URUTAN = 13

POLA_TUGAS = ("tugas", None, None, None, None)
POLA_KURS = ("kurs", None, None, None, None)
POLA_KELOMPOK = ("kelompok", None, None)


@dataclasses.dataclass(frozen=True)
class Tugas:
  """Satu permintaan konversi berisi sejumlah transaksi valuta asing.

  Tugas dikirim ke ruang sebagai tupel biasa, bukan sebagai objek, sebab ruang
  hanya mencocokkan isi tupel. Kelas ini menjaga agar urutan kolom tupel itu
  ditulis di satu tempat saja.
  """

  nomor: int
  kode_asal: str
  kode_tujuan: str
  jumlah_transaksi: int

  def ke_tupel(self) -> tuple:
    """Mengubah tugas menjadi tupel bernama tugas yang siap ditulis ke ruang.

    Kolom pertama selalu nama tupel, sehingga ruang dapat mencari tugas tanpa
    memeriksa tupel jenis lain. Mengembalikan tuple berisi lima kolom.
    """
    return ("tugas", self.nomor, self.kode_asal, self.kode_tujuan,
            self.jumlah_transaksi)

  @classmethod
  def dari_tupel(cls, tupel: tuple) -> "Tugas":
    """Membentuk kembali tugas dari tupel yang diambil processing unit.

    Kolom nama dibuang, sebab isinya pasti tugas. Mengembalikan objek Tugas.
    """
    return cls(*tupel[1:])


def tupel_kurs(versi: int = VERSI_AWAL) -> list[tuple]:
  """Menyiapkan seluruh kurs sebagai tupel siap tulis beserta nomor versinya.

  Nomor versi ikut dibawa sebagai kolom terakhir, sebab grid memori unit tidak
  punya cara lain untuk mengetahui bahwa salinannya sudah usang. Mengembalikan
  list berisi tupel lima kolom, satu tupel per pasangan mata uang.
  """
  return [("kurs", asal, tujuan, nilai, versi)
          for (asal, tujuan), nilai in KURS.items()]


def hitung_konversi(kode_asal: str, kode_tujuan: str, nominal: float,
                    kurs: float | None) -> float:
  """Mengalikan nominal dengan kurs, lalu menolak masukan yang tidak wajar.

  Kurs diterima sebagai argumen, bukan dicari sendiri, sebab pada bab ini kurs
  dibaca unit dari grid memorinya. Fungsi ini tidak perlu tahu asal kurs itu.
  Mengembalikan float berisi nilai dalam mata uang tujuan, dan melempar
  ValueError atau LookupError bila masukannya ditolak.
  """
  if nominal <= 0:
    raise ValueError("Nominal harus lebih besar dari nol")
  if kurs is None:
    raise LookupError(f"Kurs {kode_asal} ke {kode_tujuan} tidak tersedia")
  return nominal * kurs


def nominal_transaksi(nomor: int, urutan: int) -> int:
  """Membentuk nominal satu transaksi dari nomor tugas dan urutannya.

  Nominal dibentuk dengan rumus tetap agar unit mana pun menghasilkan total yang
  sama untuk tugas yang sama. Mengembalikan int antara 10 dan 1000.
  """
  return NOMINAL_TERKECIL + (nomor * PENGALI_NOMOR
                             + urutan * PENGALI_URUTAN) % RENTANG_NOMINAL


def hitung_total(tugas: Tugas, kurs: float | None) -> float:
  """Menjumlahkan nilai rupiah seluruh transaksi di dalam satu tugas.

  Perulangan inilah pekerjaan prosesor pada setiap tugas. Banyaknya transaksi
  menentukan lama satu tugas, sehingga skrip pengukuran dapat mengaturnya.
  Mengembalikan float berisi total nilai dalam mata uang tujuan.
  """
  total = 0.0
  for urutan in range(tugas.jumlah_transaksi):
    nominal = nominal_transaksi(tugas.nomor, urutan)
    total += hitung_konversi(tugas.kode_asal, tugas.kode_tujuan, nominal, kurs)
  return total


if __name__ == "__main__":
  contoh = Tugas(1, "USD", "IDR", 3)
  print(f"Tupel tugas : {contoh.ke_tupel()}")
  # Keluarannya: Tupel tugas : ('tugas', 1, 'USD', 'IDR', 3)
  print(f"Total       : {hitung_total(contoh, KURS[('USD', 'IDR')]):,.0f} IDR")
  # Keluarannya: Total       : 1,462,500 IDR
