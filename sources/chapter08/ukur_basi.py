"""Menghitung stale read yang muncul ketika replikasi kurs tertunda.

Processing unit pada versi ruang tidak membaca kurs dari ruang bersama pada
setiap tugas, melainkan dari salinannya sendiri di grid memori. Salinan itu
disegarkan berkala, dan selama jeda penyegaran unit bekerja memakai kurs lama.
Pembacaan seperti itulah yang disebut basi.

Skrip ini menyalakan satu pembaru kurs dan beberapa pembaca, lalu mengulang
percobaan yang sama untuk beberapa replication lag. Yang dilaporkan jumlah
pembacaan, jumlah stale read, dan bagiannya dalam persen.

Ruang dipakai langsung di dalam satu proses, bukan lewat proksi, sebab yang
diukur di sini keterlambatan replikasi, bukan biaya menyeberangi proses.

Cara menjalankan: python ukur_basi.py
"""

import threading
import time

import domain
import ruang

# Replication lag yang dicoba, dalam milidetik. Nilai nol berarti grid disegarkan
# tepat sebelum setiap pembacaan, dan itulah pembanding yang paling ketat.
JEDA_REPLIKASI_MS = (0, 5, 10, 25, 50, 100, 200)
# Selang penerbitan kurs baru, dalam detik. Kurs referensi sungguhan memang
# jarang berubah, tetapi selang yang pendek membuat gejalanya terlihat dalam
# percobaan yang singkat.
JEDA_PEMBARUAN = 0.05
# Lama satu percobaan untuk satu replication lag, dalam detik.
DETIK_PER_JEDA = 1.0
# Banyaknya percobaan untuk setiap replication lag. Satu percobaan saja masih
# goyah pada jeda yang panjang, sebab penerbitan kurs yang terhitung hanya dua
# puluhan kali.
PUTARAN = 3
# Jarak antar pembacaan, dalam detik. Tanpa jarak ini pembaca menghabiskan
# seluruh inti prosesor dan percobaannya berubah menjadi pengukuran kecepatan
# perulangan.
JEDA_ANTAR_BACA = 0.001
JUMLAH_PEMBACA = 4
PASANGAN_DIPANTAU = ("USD", "IDR")
LEBAR_KOLOM = (22, 14, 18, 14)


class PembacaKurs:
  """Satu processing unit yang memegang salinan kurs di grid memorinya sendiri.

  Salinan hanya disegarkan setiap replication lag. Di antara dua penyegaran,
  seluruh pembacaan dilayani dari salinan itu, walaupun kurs di ruang bersama
  sudah berganti. Kelas ini mencatat berapa kali hal tersebut terjadi.
  """

  def __init__(self, ruang_bersama: ruang.Ruang, jeda_replikasi: float) -> None:
    """Menyiapkan pencacah dan menandai bahwa grid belum pernah disegarkan.

    Nilai kurs lokal sengaja dimulai dari nol, sehingga penyegaran pertama pasti
    dijalankan sebelum pembacaan pertama.
    """
    self.ruang = ruang_bersama
    self.jeda_replikasi = jeda_replikasi
    self.nilai_lokal = 0.0
    self.versi_lokal = 0
    self.waktu_segar = 0.0
    self.jumlah_baca = 0
    self.jumlah_basi = 0

  def segarkan(self) -> None:
    """Menyalin kurs terbaru dari ruang bersama ke grid memori pembaca ini.

    Inilah satu-satunya saat pembaca menyentuh ruang untuk urusan kurs. Tidak
    mengembalikan apa pun.
    """
    tupel = self.ruang.baca(pola_pantau())
    if tupel is not None:
      self.nilai_lokal = tupel[3]
      self.versi_lokal = tupel[4]
    self.waktu_segar = time.monotonic()

  def versi_sebenarnya(self) -> int:
    """Membaca nomor versi kurs yang sedang berlaku di ruang bersama.

    Pembacaan ini alat ukur, bukan bagian dari aplikasi. Unit sungguhan tidak
    melakukannya, sebab justru itulah yang ingin dihindari. Mengembalikan int
    berisi nomor versi yang berlaku.
    """
    tupel = self.ruang.baca(pola_pantau())
    return 0 if tupel is None else tupel[4]

  def jalankan(self, tenggat: float) -> None:
    """Membaca kurs berulang kali sampai tenggat, sambil mencacah yang basi.

    Penyegaran dikerjakan hanya bila jeda replikasinya sudah terlampaui, persis
    seperti grid data yang menunggu giliran replikasi. Tidak mengembalikan apa
    pun, sebab cacahannya disimpan sebagai atribut.
    """
    while time.monotonic() < tenggat:
      if time.monotonic() - self.waktu_segar >= self.jeda_replikasi:
        self.segarkan()
      self.jumlah_baca += 1
      if self.versi_lokal != self.versi_sebenarnya():
        self.jumlah_basi += 1
      time.sleep(JEDA_ANTAR_BACA)


class PembaruKurs:
  """Penerbit kurs baru ke ruang bersama, meniru pompa data dari sisi hulu.

  Setiap penerbitan mengganti tupel kurs lama dengan tupel bernomor versi satu
  tingkat lebih tinggi. Nomor versi itulah yang membuat stale read dapat
  dihitung tanpa menebak.
  """

  def __init__(self, ruang_bersama: ruang.Ruang) -> None:
    """Menyiapkan pencacah penerbitan dengan versi awal dari domain."""
    self.ruang = ruang_bersama
    self.versi = domain.VERSI_AWAL
    self.jumlah_terbit = 0

  def terbitkan(self) -> None:
    """Mengganti tupel kurs di ruang dengan nilai dan versi yang lebih baru.

    Tupel lama diambil lebih dahulu agar ruang tidak menyimpan dua kurs untuk
    pasangan yang sama. Tidak mengembalikan apa pun.
    """
    self.versi += 1
    self.ruang.ambil(pola_pantau(), JEDA_PEMBARUAN)
    nilai_baru = domain.KURS[PASANGAN_DIPANTAU] + self.versi
    self.ruang.tulis(("kurs", PASANGAN_DIPANTAU[0], PASANGAN_DIPANTAU[1],
                      nilai_baru, self.versi))
    self.jumlah_terbit += 1

  def jalankan(self, tenggat: float) -> None:
    """Menerbitkan kurs baru berkala sampai tenggat percobaan terlewati.

    Tidak mengembalikan apa pun, sebab jumlah penerbitannya disimpan sebagai
    atribut.
    """
    while time.monotonic() < tenggat:
      self.terbitkan()
      time.sleep(JEDA_PEMBARUAN)


def pola_pantau() -> tuple:
  """Menyusun pola pencarian tupel kurs untuk pasangan yang sedang dipantau.

  Nilai dan versinya dibiarkan bebas, sebab keduanya yang justru berubah.
  Mengembalikan tuple berisi pola lima kolom.
  """
  return ("kurs", PASANGAN_DIPANTAU[0], PASANGAN_DIPANTAU[1], ruang.SEMBARANG,
          ruang.SEMBARANG)


def coba_beberapa_putaran(jeda_ms: int) -> dict:
  """Mengulang percobaan untuk satu replication lag, lalu menjumlahkan cacahannya.

  Pengulangan dipakai agar bagian basi tidak ditentukan oleh beberapa penerbitan
  kurs yang kebetulan jatuh pada saat yang menguntungkan. Mengembalikan dict
  berisi jumlah pembacaan, stale read, bagiannya, dan jumlah penerbitan.
  """
  jumlah_baca = 0
  jumlah_basi = 0
  jumlah_terbit = 0
  for _ in range(PUTARAN):
    satu = coba_satu_jeda(jeda_ms)
    jumlah_baca += satu["jumlah_baca"]
    jumlah_basi += satu["jumlah_basi"]
    jumlah_terbit += satu["jumlah_terbit"]
  return {
    "jeda_ms": jeda_ms,
    "jumlah_baca": jumlah_baca,
    "jumlah_basi": jumlah_basi,
    "bagian_basi": 100.0 * jumlah_basi / jumlah_baca if jumlah_baca else 0.0,
    "jumlah_terbit": jumlah_terbit,
  }


def coba_satu_jeda(jeda_ms: int) -> dict:
  """Menjalankan satu percobaan penuh untuk satu replication lag.

  Pembaru dan seluruh pembaca dijalankan bersamaan selama waktu yang sama, lalu
  cacahan seluruh pembaca dijumlahkan. Mengembalikan dict berisi jumlah
  pembacaan, stale read, bagiannya, dan jumlah penerbitan kurs.
  """
  ruang_bersama = ruang.Ruang()
  ruang_bersama.tulis(("kurs", PASANGAN_DIPANTAU[0], PASANGAN_DIPANTAU[1],
                       domain.KURS[PASANGAN_DIPANTAU], domain.VERSI_AWAL))
  pembaru = PembaruKurs(ruang_bersama)
  daftar_pembaca = [PembacaKurs(ruang_bersama, jeda_ms / 1000.0)
                    for _ in range(JUMLAH_PEMBACA)]
  tenggat = time.monotonic() + DETIK_PER_JEDA
  benang = [threading.Thread(target=pembaru.jalankan, args=(tenggat,))]
  benang.extend(threading.Thread(target=pembaca.jalankan, args=(tenggat,))
                for pembaca in daftar_pembaca)
  for satu in benang:
    satu.start()
  for satu in benang:
    satu.join()
  jumlah_baca = sum(pembaca.jumlah_baca for pembaca in daftar_pembaca)
  jumlah_basi = sum(pembaca.jumlah_basi for pembaca in daftar_pembaca)
  return {
    "jeda_ms": jeda_ms,
    "jumlah_baca": jumlah_baca,
    "jumlah_basi": jumlah_basi,
    "bagian_basi": 100.0 * jumlah_basi / jumlah_baca if jumlah_baca else 0.0,
    "jumlah_terbit": pembaru.jumlah_terbit,
  }


def baris_tabel(kolom: tuple) -> str:
  """Menyusun satu baris laporan dengan lebar kolom yang tetap.

  Mengembalikan str berisi satu baris siap cetak.
  """
  return "".join(f"{str(isi):>{lebar}}" for isi, lebar in zip(kolom, LEBAR_KOLOM))


if __name__ == "__main__":
  print(f"Pembaca            : {JUMLAH_PEMBACA} unit")
  print(f"Kurs terbit tiap   : {JEDA_PEMBARUAN * 1000:.0f} ms")
  print(f"Lama tiap percobaan: {DETIK_PER_JEDA:.1f} detik, {PUTARAN} putaran")
  print()
  print(baris_tabel(("Replication lag (ms)", "Pembacaan", "Stale read",
                     "Bagian basi")))
  for jeda in JEDA_REPLIKASI_MS:
    laporan = coba_beberapa_putaran(jeda)
    print(baris_tabel((laporan["jeda_ms"], laporan["jumlah_baca"],
                       laporan["jumlah_basi"],
                       f"{laporan['bagian_basi']:.1f}%")))
