"""Topologi mediator, yaitu satu mediator pusat yang memegang urutan langkah.

Publisher menaruh request pada antrean masuk mediator lalu langsung kembali.
Mediator membaca antrean itu, memanggil setiap pemroses bergantian lewat
antrean perintahnya, dan menunggu balasan sebelum melangkah ke pemroses
berikutnya. Karena urutannya tertulis pada satu daftar, mediator tahu persis
langkah mana yang gagal dan langkah mana yang belum sempat dijalankan.

Harga yang dibayar adalah message cost. Satu request menghabiskan satu
message masuk, satu perintah, dan satu balasan untuk setiap langkahnya,
sedangkan topologi broker cukup dengan satu message per langkah.

Cara menjalankan: python mediator.py
"""

import queue
import threading

import domain
import pemroses

# Urutan langkah yang dipegang mediator. Inilah pengetahuan terpusat yang tidak
# dimiliki topologi broker, dan inilah pula yang harus disunting ketika satu
# pemroses baru disisipkan.
URUTAN_LANGKAH = ("recorder", "validator", "notifier")

# Penanda khusus yang menyuruh thread berhenti, sama seperti pada broker.py.
PENANDA_BERHENTI = object()

# Batas tunggu saat menutup mediator, dalam detik.
BATAS_TUTUP = 2.0


class Mediator:
  """Mediator pusat yang menjalankan urutan langkah bagi setiap request.

  Mediator berjalan di threadnya sendiri dan menangani satu request pada
  satu waktu. Pilihan itu membuat urutannya terjaga rapi, sekaligus membuat
  mediator menjadi satu-satunya leher botol ketika salah satu pemroses lambat.
  """

  def __init__(self, urutan=URUTAN_LANGKAH) -> None:
    """Menyiapkan antrean masuk, antrean balasan, lalu menyalakan threadnya.

    Thread mediator langsung berjalan dan menunggu di antrean masuk, sehingga
    pendaftaran pemroses yang menyusul tetap sempat selesai sebelum request
    pertama datang.
    """
    self.urutan = list(urutan)
    self.antrean_masuk = queue.Queue()
    self.antrean_balasan = queue.Queue()
    self.antrean_perintah = {}
    self.pemroses = {}
    self.thread = []
    self.jumlah_pesan = 0
    self.gagal = []
    self.kunci = threading.Lock()
    self.utas_mediator = threading.Thread(target=self.layani_mediator,
                                          daemon=True)
    self.utas_mediator.start()

  def hitung_pesan(self, jumlah: int) -> None:
    """Menambah pencacah message sebanyak jumlah yang baru saja dikirim."""
    with self.kunci:
      self.jumlah_pesan += jumlah

  def jumlah_langkah(self) -> int:
    """Mengembalikan int panjang urutan langkah yang dipegang mediator ini."""
    return len(self.urutan)

  def pemroses_bernama(self, nama: str):
    """Mengembalikan objek pemroses yang namanya diminta, untuk pemeriksaan.

    Mediator memang menyimpan rujukan ke setiap pemrosesnya, dan justru itulah
    yang membedakannya dari broker, yang hanya mengenal antrean.
    """
    return self.pemroses[nama]

  def daftarkan(self, nama: str, pemroses_baru) -> queue.Queue:
    """Membuat satu antrean perintah beserta threadnya bagi satu pemroses.

    Mengembalikan objek Queue milik pemroses itu. Mediator memanggilnya lewat
    antrean, bukan lewat pemanggilan langsung, agar setiap langkah berupa message
    yang dapat dihitung.
    """
    antrean = queue.Queue()
    self.antrean_perintah[nama] = antrean
    self.pemroses[nama] = pemroses_baru
    utas = threading.Thread(target=self.layani_pemroses,
                            args=(nama, antrean, pemroses_baru), daemon=True)
    utas.start()
    self.thread.append((antrean, utas))
    return antrean

  def layani_pemroses(self, nama: str, antrean: queue.Queue,
                      pemroses_baru) -> None:
    """Menjalankan satu pemroses sampai penanda berhenti diterimanya.

    Hasilnya selalu dibalas ke mediator, baik berhasil maupun gagal. Balasan
    itulah yang membuat mediator dapat menghentikan sisa langkah tanpa menunggu
    batas waktu.
    """
    while True:
      pesan = antrean.get()
      if pesan is PENANDA_BERHENTI:
        return
      try:
        pemroses_baru.tangani(pesan)
        galat = None
      except Exception as kesalahan:
        galat = str(kesalahan)
      self.antrean_balasan.put((nama, pesan, galat))
      self.hitung_pesan(1)

  def layani_mediator(self) -> None:
    """Membaca antrean masuk lalu menjalankan urutan langkah satu per satu."""
    while True:
      request = self.antrean_masuk.get()
      if request is PENANDA_BERHENTI:
        return
      self.jalankan_urutan(request)

  def jalankan_urutan(self, request: domain.Request) -> bool:
    """Memanggil setiap pemroses bergantian, lalu berhenti pada error pertama.

    Mengembalikan bool bernilai True bila seluruh langkah selesai. Bila gagal,
    nomor request, nama langkahnya, dan sisa langkah yang belum dijalankan
    dicatat pada daftar gagal, sebab hanya mediator yang mengetahui ketiganya.
    """
    for nomor_langkah, nama in enumerate(self.urutan):
      self.antrean_perintah[nama].put(request)
      self.hitung_pesan(1)
      _, _, galat = self.antrean_balasan.get()
      if galat is not None:
        sisa = self.urutan[nomor_langkah + 1:]
        self.gagal.append((request.nomor, nama, list(sisa)))
        return False
    return True

  def kirim(self, request: domain.Request) -> domain.Request:
    """Menaruh request pada antrean masuk lalu kembali tanpa menunggu.

    Mengembalikan objek request yang sama, yang saat itu belum tentu sudah
    diproses. Pemanggil yang ingin menunggu hasilnya memakai request.tunggu().
    """
    self.antrean_masuk.put(request)
    self.hitung_pesan(1)
    return request

  def pesan_terkirim(self) -> int:
    """Mengembalikan int jumlah message yang sudah melewati seluruh antrean."""
    return self.jumlah_pesan

  def antrean_backlog(self) -> int:
    """Mengembalikan int jumlah message yang masih menunggu di seluruh antrean.

    Antrean masuk mediatorlah yang biasanya menumpuk, sebab seluruh request
    melewati satu pintu yang sama.
    """
    backlog = self.antrean_masuk.qsize() + self.antrean_balasan.qsize()
    return backlog + sum(a.qsize() for a in self.antrean_perintah.values())

  def galat_tercatat(self) -> int:
    """Mengembalikan int jumlah request yang urutannya putus di tengah."""
    return len(self.gagal)

  def contoh_galat(self):
    """Mengembalikan str catatan gagal pertama, atau None bila belum ada.

    Catatannya memuat langkah yang gagal sekaligus sisa langkah yang belum
    sempat dijalankan, sebab hanya mediator yang memegang urutan lengkapnya.
    """
    if not self.gagal:
      return None
    nomor, langkah, sisa = self.gagal[0]
    return f"request {nomor} putus pada {langkah}, sisa {sisa}"

  def tutup(self) -> None:
    """Menghentikan thread mediator beserta seluruh thread pemrosesnya."""
    self.antrean_masuk.put(PENANDA_BERHENTI)
    self.utas_mediator.join(BATAS_TUTUP)
    for antrean, _ in self.thread:
      antrean.put(PENANDA_BERHENTI)
    for _, utas in self.thread:
      utas.join(BATAS_TUTUP)


def rakit(validator=None) -> Mediator:
  """Merangkai mediator beserta ketiga pemroses yang diaturnya.

  Urutan langkahnya diambil dari URUTAN_LANGKAH, dan nama pada daftar itu harus
  sama dengan nama yang didaftarkan di bawah. Mengembalikan objek Mediator yang
  threadnya sudah berjalan dan siap menerima request.
  """
  mediator = Mediator(URUTAN_LANGKAH)
  mediator.daftarkan("recorder", pemroses.Recorder())
  mediator.daftarkan("validator", validator or pemroses.Validator())
  mediator.daftarkan("notifier", pemroses.Notifier())
  return mediator


if __name__ == "__main__":
  susunan = rakit()
  contoh = domain.buat_request(31, susunan.jumlah_langkah())
  susunan.kirim(contoh)
  contoh.tunggu(BATAS_TUTUP)
  print(contoh.pemberitahuan)
  # Keluarannya: Request 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Message lewat antrean: {susunan.pesan_terkirim()}")
  # Keluarannya: Message lewat antrean: 7
  susunan.tutup()
