"""Virtualized middleware, yaitu bagian yang mengurus segala hal antar unit.

Richards dan Ford membaginya menjadi empat, yaitu messaging grid, data grid,
processing grid, dan deployment manager. Data grid berada di grid.py sebab
isinya memang salinan data. Tiga sisanya ada di file ini.

Messaging grid membagikan request kepada unit yang sedang menganggur.
Deployment manager menyalakan unit baru ketika antreannya memanjang. Richards
dan Ford juga menugasinya mematikan unit ketika beban turun, dan bagian itu
tidak dibuat sebab pengukuran bab ini tidak memakainya. Processing grid hanya
dibutuhkan bila satu request harus melewati beberapa jenis unit, dan bab ini
tidak memakainya sebab seluruh unitnya sejenis.

Cara menjalankan: python middleware.py
"""

import dataclasses
import multiprocessing
import os
import queue
import threading
import time

# Panjang antrean yang dianggap sebagai tanda beban naik. Angkanya kecil agar
# penyalaan unit baru terlihat pada percobaan yang singkat.
BATAS_ANTREAN_NAIK = 8
# Jarak antar pemeriksaan beban oleh deployment manager, dalam detik.
JEDA_PANTAU = 0.05
# Lama menunggu catatan satu unit sebelum pengumpulannya dinyatakan gagal,
# dalam detik. Angkanya longgar, sebab versi basis data pada cakram yang lambat
# dapat memakan belasan detik untuk satu putaran.
BATAS_TUNGGU_CATATAN = 300.0
# Lama replikator menunggu titipan berikutnya sebelum memeriksa ulang hubnya.
BATAS_TUNGGU_HUB = 0.05
# Nilai panjang antrean pada sistem operasi yang tidak dapat menghitungnya,
# misalnya macOS, yang tidak menyediakan sem_getvalue bagi antrean antarproses.
PANJANG_TIDAK_TERHITUNG = -1
# Banyaknya request, batas unit, dan lama tunggu pada contoh di bawah.
JUMLAH_CONTOH = 12
BATAS_UNIT_CONTOH = 4
LAMA_PANTAU_CONTOH = JEDA_PANTAU * 4
BATAS_AMBIL_CONTOH = 0.2


def kunci_ke_inti(inti: int) -> None:
  """Mengunci proses pemanggil pada satu prosesor saja.

  Pengukuran hasil menuntut tiap unit memakai prosesornya sendiri, sehingga
  selisih antar jumlah unit tidak tercampur perebutan inti. Nilai None berarti
  tidak dikunci. Penguncian dilewati pada sistem operasi yang tidak
  menyediakannya, misalnya Windows dan macOS, dan pada nomor prosesor yang
  tidak ada di mesin itu. Tidak mengembalikan apa pun.
  """
  if inti is None:
    return
  if not hasattr(os, "sched_setaffinity"):
    return
  prosesor_tersedia = os.sched_getaffinity(0)
  if inti not in prosesor_tersedia:
    return
  os.sched_setaffinity(0, {inti})


def jalankan_replikator_proses(saluran, inti: int, gerbang) -> None:
  """Menyebarkan titipan replikasi dari hub ke kotak masuk seluruh unit.

  Proses ini memindahkan biaya penyebaran keluar dari unit. Unit cukup
  menitipkan satu message, lalu proses inilah yang menyalinnya sebanyak unit
  yang ada, memakai prosesornya sendiri. Berhenti ketika menerima penanda
  None. Tidak mengembalikan apa pun.
  """
  kunci_ke_inti(inti)
  gerbang.wait()
  while True:
    titipan = saluran.ambil_dari_hub(BATAS_TUNGGU_HUB)
    if titipan is None:
      continue
    nomor_pengirim, pesan = titipan
    if pesan is None:
      break
    saluran.sebarkan(nomor_pengirim, pesan)
  saluran.lepas_tanpa_menunggu()


class MessagingGrid:
  """Pembagi request kepada processing unit yang sedang menganggur.

  Wujudnya satu antrean bersama. Unit yang bebas mengambil request berikutnya,
  sehingga pembagiannya mengikuti siapa yang lebih dahulu selesai, bukan
  giliran yang ditetapkan di muka. Antrean inilah yang panjangnya dipantau
  deployment manager.

  Antreannya multiprocessing.Queue, sehingga unit yang berjalan sebagai proses
  tersendiri pun mengambil dari antrean yang sama. Biaya memindahkan request
  lewat antrean ini diukur ukur_hasil.py sebagai batas messaging grid, sebab
  biaya itulah batas atas hasil versi space berapa pun unitnya.
  """

  def __init__(self) -> None:
    """Menyiapkan antrean request sebelum proses unit dinyalakan.

    Antrean antarproses harus sudah ada sebelum prosesnya dibuat, sebab
    antrean itu diwariskan lewat argumen proses, bukan dicari belakangan.
    """
    self.antrean = multiprocessing.Queue()

  def kirim(self, request) -> None:
    """Menaruh satu request ke antrean beserta waktu masuknya.

    Waktu masuk dibubuhkan di sini, sehingga latensi yang terukur nanti
    mencakup lama menunggu giliran, bukan hanya lama dikerjakan. Tidak
    mengembalikan apa pun.
    """
    waktu_kirim = time.monotonic()
    request_berwaktu = dataclasses.replace(request, waktu_kirim=waktu_kirim)
    self.antrean.put(request_berwaktu)

  def ambil(self, batas_tunggu: float):
    """Mengambil satu request bagi unit yang sedang menganggur.

    Mengembalikan Request bila ada, atau None bila antreannya kosong sampai
    batas tunggunya lewat.
    """
    try:
      return self.antrean.get(timeout=batas_tunggu)
    except queue.Empty:
      return None

  def panjang(self) -> int:
    """Menghitung request yang sedang menunggu giliran di antrean.

    Angka inilah yang dibaca deployment manager sebagai tanda beban.
    Mengembalikan int berisi jumlah request yang menunggu, atau
    PANJANG_TIDAK_TERHITUNG pada sistem operasi yang tidak dapat menghitungnya.
    """
    try:
      return self.antrean.qsize()
    except NotImplementedError:
      return PANJANG_TIDAK_TERHITUNG


class Pencatat:
  """Tempat setiap processing unit menitipkan hasil hitungannya sebelum mati.

  Unit yang berjalan sebagai proses tersendiri tidak dapat menyerahkan
  pencacahnya lewat atribut biasa, sebab atribut itu hidup di proses lain.
  Hasilnya karena itu dikirim lewat antrean, lalu dikumpulkan pemanggilnya
  sesudah seluruh unit selesai.
  """

  def __init__(self) -> None:
    """Menyiapkan antrean catatan sebelum proses unit dinyalakan.

    Seperti antrean lain di file ini, antrean catatan harus dibuat lebih
    dahulu agar dapat diwariskan kepada proses unit.
    """
    self.antrean = multiprocessing.Queue()

  def catat(self, nama: str, dilayani: int, ditolak: int, daftar_lama: list,
            waktu_selesai: float) -> None:
    """Menyimpan hasil satu unit, yaitu cacahan, latensi, dan waktu selesai.

    Waktu selesai dicatat unitnya sendiri, sehingga lama satu putaran dihitung
    sampai unit terakhir berhenti bekerja, bukan sampai catatannya sampai ke
    pemanggil. Tidak mengembalikan apa pun.
    """
    self.antrean.put((nama, dilayani, ditolak, daftar_lama, waktu_selesai))

  def ringkas(self, jumlah_unit: int,
              batas_tunggu: float = BATAS_TUNGGU_CATATAN) -> tuple:
    """Menunggu catatan sebanyak unit yang dijalankan lalu menggabungkannya.

    Catatan dikumpulkan sebelum prosesnya ditunggu selesai, sebab proses yang
    sudah menaruh message besar di antrean tidak dapat berakhir sampai message-nya
    terbaca. Melempar RuntimeError bila satu catatan tidak datang sampai batas
    tunggunya lewat, sebab hasil yang tidak lengkap lebih berbahaya daripada
    tidak ada hasil sama sekali. Mengembalikan tuple berisi jumlah dilayani,
    jumlah ditolak, daftar latensi seluruh unit, dan waktu selesai unit yang
    paling akhir.
    """
    dilayani = 0
    ditolak = 0
    daftar_latensi = []
    waktu_selesai = 0.0
    for _ in range(jumlah_unit):
      try:
        catatan = self.antrean.get(timeout=batas_tunggu)
      except queue.Empty as kosong:
        pesan_galat = (f"catatan unit tidak datang dalam {batas_tunggu:.0f} "
                       f"detik")
        raise RuntimeError(pesan_galat) from kosong
      dilayani += catatan[1]
      ditolak += catatan[2]
      daftar_latensi.extend(catatan[3])
      waktu_selesai = max(waktu_selesai, catatan[4])
    return dilayani, ditolak, daftar_latensi, waktu_selesai


class DeploymentManager:
  """Penyala processing unit baru mengikuti panjang antrean.

  Inilah bagian yang membuat susunan ini disebut elastis. Pemantauannya
  sederhana, yaitu antrean yang memanjang dibaca sebagai beban naik, lalu satu
  unit baru dinyalakan sampai batas yang diizinkan.
  """

  def __init__(self, messaging_grid: MessagingGrid, penyala, batas_unit: int,
               unit_awal: int) -> None:
    """Menyimpan cara menyalakan unit beserta batas jumlahnya.

    Penyala berupa fungsi yang membuat satu unit baru lalu menjalankannya,
    sehingga deployment manager tidak perlu mengenal isi unitnya.
    """
    self.messaging_grid = messaging_grid
    self.penyala = penyala
    self.batas_unit = batas_unit
    self.jumlah_unit = unit_awal
    self.jumlah_dinyalakan = 0
    self.berhenti = threading.Event()
    self.utas = None

  def mulai(self) -> None:
    """Menjalankan pemantauan beban pada thread tersendiri.

    Pemantauan dipisah dari pembagian request, sehingga messaging grid tetap
    membagikan request walaupun pemantaunya sedang menyalakan unit. Tidak
    mengembalikan apa pun.
    """
    self.utas = threading.Thread(target=self.pantau, daemon=True)
    self.utas.start()

  def pantau(self) -> None:
    """Memeriksa panjang antrean berkala lalu menyalakan unit bila perlu.

    Tidak mengembalikan apa pun.
    """
    while not self.berhenti.wait(JEDA_PANTAU):
      panjang = self.messaging_grid.panjang()
      if panjang >= BATAS_ANTREAN_NAIK and self.jumlah_unit < self.batas_unit:
        self.penyala()
        self.jumlah_unit += 1
        self.jumlah_dinyalakan += 1

  def hentikan(self) -> None:
    """Menghentikan pemantauan lalu menunggu threadnya selesai.

    Unit yang sudah dinyalakan tidak ikut dimatikan, sebab mematikannya adalah
    keputusan pemanggil. Tidak mengembalikan apa pun.
    """
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=1.0)


def nyalakan_unit_contoh() -> None:
  """Berpura-pura menyalakan satu unit baru bagi contoh di bawah.

  Deployment manager hanya memanggil fungsi penyala, sehingga contohnya cukup
  mencacah berapa kali panggilan itu terjadi. Tidak mengembalikan apa pun.
  """
  DINYALAKAN.append(1)


DINYALAKAN = []


if __name__ == "__main__":
  import domain

  grid_pesan = MessagingGrid()
  for request_contoh in domain.bangkitkan_request(JUMLAH_CONTOH):
    grid_pesan.kirim(request_contoh)
  print(f"Request menunggu     : {grid_pesan.panjang()}")

  manajer = DeploymentManager(grid_pesan, nyalakan_unit_contoh,
                              batas_unit=BATAS_UNIT_CONTOH, unit_awal=1)
  manajer.mulai()
  time.sleep(LAMA_PANTAU_CONTOH)
  diambil = 0
  while grid_pesan.ambil(BATAS_AMBIL_CONTOH) is not None:
    diambil += 1
  manajer.hentikan()
  print(f"Request terambil     : {diambil}")
  print(f"Unit dinyalakan      : {manajer.jumlah_dinyalakan}")
  # Keluarannya baris terakhir: Unit dinyalakan      : 3
