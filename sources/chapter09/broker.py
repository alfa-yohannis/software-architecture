"""Topologi broker, yaitu rangkaian event tanpa satu pun mediator pusat.

Publisher menaruh satu event pada broker lalu langsung kembali. Setiap subscriber
punya antrean dan thread sendiri, menangani event yang menjadi bagiannya, lalu
menerbitkan event lanjutan. Urutan langkahnya karena itu tidak tertulis di satu
tempat, melainkan tersebar pada pilihan topic setiap subscriber.

Brokernya dibuat dari queue.Queue dan threading, tanpa pustaka pihak ketiga,
agar seluruh latihan berjalan pada satu laptop. Broker sungguhan seperti Kafka
menambahkan storage tahan mati, pembagian partisi, dan pengulangan kiriman,
tetapi bentuk berlangganannya sama.

Cara menjalankan: python broker.py
"""

import queue
import threading

import domain
import pemroses

TOPIC_RECEIVED = "request.received"
TOPIC_RECORDED = "request.recorded"
TOPIC_VALIDATED = "request.validated"

# Penanda khusus yang menyuruh thread subscriber berhenti. Objek kosong dipakai
# agar tidak mungkin tertukar dengan request yang sah.
PENANDA_BERHENTI = object()

# Batas tunggu saat menutup broker, dalam detik. Thread yang belum berhenti
# sesudah itu dibiarkan mati sendiri, sebab seluruhnya daemon.
BATAS_TUTUP = 2.0


class Broker:
  """Penyalur event yang hanya mengenal topic, bukan isi pekerjaannya.

  Setiap subscriber mendapat satu antrean dan satu thread tersendiri, sehingga
  subscriber yang lambat hanya menahan antreannya sendiri.
  Error subscriber ditangkap lalu dicatat, sebab satu subscriber yang jatuh tidak
  boleh menghentikan penyaluran event bagi subscriber lain.
  """

  def __init__(self) -> None:
    """Menyiapkan daftar langganan kosong beserta pencacah message dan error."""
    self.langganan_topic = {}
    self.thread = []
    self.jumlah_pesan = 0
    self.galat = []
    self.kunci = threading.Lock()

  def langganan(self, topic: str, penangan) -> queue.Queue:
    """Mendaftarkan satu subscriber pada satu topic beserta threadnya.

    Mengembalikan objek Queue milik subscriber itu, sehingga pemanggil dapat
    memeriksa kedalaman antreannya. Broker sendiri tidak pernah tahu apa yang
    dikerjakan penangannya.
    """
    antrean = queue.Queue()
    self.langganan_topic.setdefault(topic, []).append(antrean)
    utas = threading.Thread(target=self.layani, daemon=True,
                            args=(topic, antrean, penangan))
    utas.start()
    self.thread.append((antrean, utas))
    return antrean

  def layani(self, topic: str, antrean: queue.Queue, penangan) -> None:
    """Menjalankan satu subscriber sampai penanda berhenti diterimanya.

    Error penangan ditangkap lalu disimpan pada daftar error broker. Akibatnya,
    event lanjutan tidak pernah terbit, dan rangkaian di belakangnya berhenti
    tanpa satu pun pihak yang mengetahuinya.
    """
    while True:
      pesan = antrean.get()
      if pesan is PENANDA_BERHENTI:
        return
      try:
        penangan(pesan)
      except Exception as kesalahan:
        with self.kunci:
          self.galat.append((topic, pesan.nomor, str(kesalahan)))

  def terbitkan(self, topic: str, pesan: domain.Request) -> int:
    """Menaruh message pada antrean setiap subscriber topic tersebut.

    Mengembalikan int berisi jumlah subscriber yang menerima message itu. Topic
    tanpa subscriber dijawab nol tanpa error, persis seperti broker sungguhan.
    """
    antrean_subscriber = self.langganan_topic.get(topic, [])
    for antrean in antrean_subscriber:
      antrean.put(pesan)
    with self.kunci:
      self.jumlah_pesan += len(antrean_subscriber)
    return len(antrean_subscriber)

  def antrean_backlog(self) -> int:
    """Mengembalikan int jumlah message yang masih menunggu di seluruh antrean.

    Angka inilah yang naik ketika satu subscriber lebih lambat daripada
    publisher-nya, dan angka itulah yang dicatat pada uji ketahanan.
    """
    return sum(antrean.qsize()
               for daftar in self.langganan_topic.values()
               for antrean in daftar)

  def jumlah_subscriber(self) -> int:
    """Mengembalikan int jumlah subscriber yang terdaftar pada seluruh topic."""
    return sum(len(daftar) for daftar in self.langganan_topic.values())

  def tutup(self) -> None:
    """Menghentikan seluruh thread subscriber dengan mengirim penanda berhenti."""
    for antrean, _ in self.thread:
      antrean.put(PENANDA_BERHENTI)
    for _, utas in self.thread:
      utas.join(BATAS_TUTUP)


class SusunanBroker:
  """Ketiga pemroses yang berlangganan sendiri-sendiri pada broker yang sama.

  Setiap penangan mengerjakan bagiannya lalu menerbitkan event lanjutan, dan
  tidak satu pun di antaranya menyebut nama subscriber berikutnya. Urutan
  langkah karena itu hanya terbaca dari pasangan topic yang dipakai, bukan dari
  satu daftar terpusat.
  """

  def __init__(self, broker: Broker, recorder, validator, notifier) -> None:
    """Menyimpan broker beserta ketiga pemroses yang akan dilangganankan."""
    self.broker = broker
    self.recorder = recorder
    self.validator = validator
    self.notifier = notifier

  def jumlah_langkah(self) -> int:
    """Mengembalikan int jumlah langkah, yaitu banyaknya subscriber terdaftar.

    Angkanya dihitung dari daftar langganan broker, bukan ditulis sebagai
    tetapan. Karena itu, menambah subscriber baru tidak menyunting kelas ini.
    """
    return self.broker.jumlah_subscriber()

  def pemroses_bernama(self, nama: str):
    """Mengembalikan objek pemroses yang namanya diminta, untuk pemeriksaan."""
    return getattr(self, nama)

  def saat_received(self, request: domain.Request) -> None:
    """Mencatat request, lalu mengumumkan bahwa pencatatannya selesai."""
    self.recorder.tangani(request)
    self.broker.terbitkan(TOPIC_RECORDED, request)

  def saat_recorded(self, request: domain.Request) -> None:
    """Memeriksa request, lalu mengumumkan bahwa pemeriksaannya selesai."""
    self.validator.tangani(request)
    self.broker.terbitkan(TOPIC_VALIDATED, request)

  def saat_validated(self, request: domain.Request) -> None:
    """Menyusun pemberitahuan sebagai langkah terakhir rangkaian ini."""
    self.notifier.tangani(request)

  def kirim(self, request: domain.Request) -> domain.Request:
    """Menerbitkan satu event lalu kembali tanpa menunggu pekerjaan selesai.

    Mengembalikan objek request yang sama, yang saat itu belum tentu sudah
    diproses. Pemanggil yang ingin menunggu hasilnya memakai request.tunggu().
    """
    self.broker.terbitkan(TOPIC_RECEIVED, request)
    return request

  def pesan_terkirim(self) -> int:
    """Mengembalikan int jumlah message yang sudah melewati antrean broker."""
    return self.broker.jumlah_pesan

  def antrean_backlog(self) -> int:
    """Mengembalikan int jumlah message yang masih menunggu di seluruh antrean."""
    return self.broker.antrean_backlog()

  def galat_tercatat(self) -> int:
    """Mengembalikan int jumlah error subscriber yang tercatat pada broker."""
    return len(self.broker.galat)

  def contoh_galat(self):
    """Mengembalikan str catatan error pertama, atau None bila belum ada.

    Catatannya hanya mengenal topic dan nomor request, sebab broker tidak
    pernah tahu ada langkah lain di belakang subscriber yang gagal itu.
    """
    if not self.broker.galat:
      return None
    topic, nomor, pesan = self.broker.galat[0]
    return f"topic {topic}, request {nomor}: {pesan}"

  def tutup(self) -> None:
    """Menghentikan seluruh thread subscriber lewat broker yang dipegangnya."""
    self.broker.tutup()


def rakit(validator=None) -> SusunanBroker:
  """Merangkai broker, ketiga pemroses, lalu ketiga langganannya.

  Seluruh pengetahuan tentang urutan langkah berada di dalam tiga baris
  langganan di bawah ini. Mengembalikan objek SusunanBroker yang threadnya
  sudah berjalan dan siap menerima request.
  """
  penyalur = Broker()
  susunan = SusunanBroker(penyalur, pemroses.Recorder(),
                          validator or pemroses.Validator(),
                          pemroses.Notifier())
  penyalur.langganan(TOPIC_RECEIVED, susunan.saat_received)
  penyalur.langganan(TOPIC_RECORDED, susunan.saat_recorded)
  penyalur.langganan(TOPIC_VALIDATED, susunan.saat_validated)
  return susunan


if __name__ == "__main__":
  susunan = rakit()
  contoh = domain.buat_request(31, susunan.jumlah_langkah())
  susunan.kirim(contoh)
  contoh.tunggu(BATAS_TUTUP)
  print(contoh.pemberitahuan)
  # Keluarannya: Request 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Message lewat antrean: {susunan.pesan_terkirim()}")
  # Keluarannya: Message lewat antrean: 3
  susunan.tutup()
