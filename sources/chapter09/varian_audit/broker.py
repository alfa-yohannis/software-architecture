"""Varian topologi broker sesudah pencatat audit disisipkan.

Berkas ini adalah salinan broker.py yang sudah memuat satu pelanggan baru,
yaitu PencatatAudit dari audit.py. Pelanggan baru itu berlangganan pada topik
yang sudah ada, yaitu permintaan.diterima, sehingga ia berjalan sejajar dengan
pencatat dan tidak menunggu giliran.

Perhatikan bahwa tidak ada satu pun penangan lama yang disunting. Yang berubah
hanya bagian perakitannya, sebab urutan langkah pada topologi ini memang tidak
tertulis di satu tempat.

Cara menjalankan: python -m varian_audit.broker
"""

import queue
import threading

import audit
import domain
import pemroses

TOPIK_DITERIMA = "permintaan.diterima"
TOPIK_DICATAT = "permintaan.dicatat"
TOPIK_DIPERIKSA = "permintaan.diperiksa"

# Penanda khusus yang menyuruh thread pelanggan berhenti. Objek kosong dipakai
# agar tidak mungkin tertukar dengan permintaan yang sah.
PENANDA_BERHENTI = object()

# Batas tunggu saat menutup broker, dalam detik. Thread yang belum berhenti
# sesudah itu dibiarkan mati sendiri, sebab seluruhnya daemon.
BATAS_TUTUP = 2.0


class Broker:
  """Penyalur event yang hanya mengenal topik, bukan isi pekerjaannya.

  Setiap pelanggan mendapat satu antrean dan satu thread tersendiri, sehingga
  pelanggan yang lambat menahan antreannya sendiri, bukan antrean tetangganya.
  Galat pelanggan ditangkap lalu dicatat, sebab satu pelanggan yang jatuh tidak
  boleh menghentikan penyaluran event bagi pelanggan lain.
  """

  def __init__(self) -> None:
    """Menyiapkan daftar langganan kosong beserta pencacah pesan dan galat."""
    self.langganan_topik = {}
    self.thread = []
    self.jumlah_pesan = 0
    self.galat = []
    self.kunci = threading.Lock()

  def langganan(self, topik: str, penangan) -> queue.Queue:
    """Mendaftarkan satu pelanggan pada satu topik beserta threadnya.

    Mengembalikan objek Queue milik pelanggan itu, sehingga pemanggil dapat
    memeriksa kedalaman antreannya. Broker sendiri tidak pernah tahu apa yang
    dikerjakan penangannya.
    """
    antrean = queue.Queue()
    self.langganan_topik.setdefault(topik, []).append(antrean)
    utas = threading.Thread(target=self.layani, daemon=True,
                            args=(topik, antrean, penangan))
    utas.start()
    self.thread.append((antrean, utas))
    return antrean

  def layani(self, topik: str, antrean: queue.Queue, penangan) -> None:
    """Menjalankan satu pelanggan sampai penanda berhenti diterimanya.

    Galat penangan ditangkap lalu disimpan pada daftar galat broker. Akibatnya,
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
          self.galat.append((topik, pesan.nomor, str(kesalahan)))

  def terbitkan(self, topik: str, pesan: domain.Permintaan) -> int:
    """Menaruh pesan pada antrean setiap pelanggan topik tersebut.

    Mengembalikan int berisi jumlah pelanggan yang menerima pesan itu. Topik
    tanpa pelanggan dijawab nol tanpa galat, persis seperti broker sungguhan.
    """
    antrean_pelanggan = self.langganan_topik.get(topik, [])
    for antrean in antrean_pelanggan:
      antrean.put(pesan)
    with self.kunci:
      self.jumlah_pesan += len(antrean_pelanggan)
    return len(antrean_pelanggan)

  def antrean_tertahan(self) -> int:
    """Mengembalikan int jumlah pesan yang masih menunggu di seluruh antrean.

    Angka inilah yang naik ketika satu pelanggan lebih lambat daripada
    penerbitnya, dan angka itulah yang dicatat pada uji ketahanan.
    """
    return sum(antrean.qsize()
               for daftar in self.langganan_topik.values()
               for antrean in daftar)

  def jumlah_pelanggan(self) -> int:
    """Mengembalikan int jumlah pelanggan yang terdaftar pada seluruh topik."""
    return sum(len(daftar) for daftar in self.langganan_topik.values())

  def tutup(self) -> None:
    """Menghentikan seluruh thread pelanggan dengan mengirim penanda berhenti."""
    for antrean, _ in self.thread:
      antrean.put(PENANDA_BERHENTI)
    for _, utas in self.thread:
      utas.join(BATAS_TUTUP)


class SusunanBroker:
  """Ketiga pemroses yang berlangganan sendiri-sendiri pada broker yang sama.

  Setiap penangan mengerjakan bagiannya lalu menerbitkan event lanjutan, dan
  tidak satu pun di antaranya menyebut nama pelanggan berikutnya. Urutan
  langkah karena itu hanya terbaca dari pasangan topik yang dipakai, bukan dari
  satu daftar terpusat.
  """

  def __init__(self, broker: Broker, pencatat, pemeriksa, pemberitahu) -> None:
    """Menyimpan broker beserta ketiga pemroses yang akan dilangganankan."""
    self.broker = broker
    self.pencatat = pencatat
    self.pemeriksa = pemeriksa
    self.pemberitahu = pemberitahu

  def jumlah_langkah(self) -> int:
    """Mengembalikan int jumlah langkah, yaitu banyaknya pelanggan terdaftar.

    Angkanya dihitung dari daftar langganan broker, bukan ditulis sebagai
    tetapan. Karena itu, menambah pelanggan baru tidak menyunting kelas ini.
    """
    return self.broker.jumlah_pelanggan()

  def pemroses_bernama(self, nama: str):
    """Mengembalikan objek pemroses yang namanya diminta, untuk pemeriksaan."""
    return getattr(self, nama)

  def saat_diterima(self, permintaan: domain.Permintaan) -> None:
    """Mencatat permintaan, lalu mengumumkan bahwa pencatatannya selesai."""
    self.pencatat.tangani(permintaan)
    self.broker.terbitkan(TOPIK_DICATAT, permintaan)

  def saat_dicatat(self, permintaan: domain.Permintaan) -> None:
    """Memeriksa permintaan, lalu mengumumkan bahwa pemeriksaannya selesai."""
    self.pemeriksa.tangani(permintaan)
    self.broker.terbitkan(TOPIK_DIPERIKSA, permintaan)

  def saat_diperiksa(self, permintaan: domain.Permintaan) -> None:
    """Menyusun pemberitahuan sebagai langkah terakhir rangkaian ini."""
    self.pemberitahu.tangani(permintaan)

  def kirim(self, permintaan: domain.Permintaan) -> domain.Permintaan:
    """Menerbitkan satu event lalu kembali tanpa menunggu pekerjaan selesai.

    Mengembalikan objek permintaan yang sama, yang saat itu belum tentu sudah
    diproses. Pemanggil yang ingin menunggu hasilnya memakai permintaan.tunggu().
    """
    self.broker.terbitkan(TOPIK_DITERIMA, permintaan)
    return permintaan

  def pesan_terkirim(self) -> int:
    """Mengembalikan int jumlah pesan yang sudah melewati antrean broker."""
    return self.broker.jumlah_pesan

  def antrean_tertahan(self) -> int:
    """Mengembalikan int jumlah pesan yang masih menunggu di seluruh antrean."""
    return self.broker.antrean_tertahan()

  def galat_tercatat(self) -> int:
    """Mengembalikan int jumlah galat pelanggan yang tercatat pada broker."""
    return len(self.broker.galat)

  def contoh_galat(self):
    """Mengembalikan str catatan galat pertama, atau None bila belum ada.

    Catatannya hanya mengenal topik dan nomor permintaan, sebab broker tidak
    pernah tahu ada langkah lain di belakang pelanggan yang gagal itu.
    """
    if not self.broker.galat:
      return None
    topik, nomor, pesan = self.broker.galat[0]
    return f"topik {topik}, permintaan {nomor}: {pesan}"

  def tutup(self) -> None:
    """Menghentikan seluruh thread pelanggan lewat broker yang dipegangnya."""
    self.broker.tutup()


def rakit(pemeriksa=None) -> SusunanBroker:
  """Merangkai broker, ketiga pemroses, lalu ketiga langganannya.

  Seluruh pengetahuan tentang urutan langkah berada di dalam tiga baris
  langganan di bawah ini. Mengembalikan objek SusunanBroker yang threadnya
  sudah berjalan dan siap menerima permintaan.
  """
  penyalur = Broker()
  susunan = SusunanBroker(penyalur, pemroses.Pencatat(),
                          pemeriksa or pemroses.Pemeriksa(),
                          pemroses.Pemberitahu())
  penyalur.langganan(TOPIK_DITERIMA, susunan.saat_diterima)
  penyalur.langganan(TOPIK_DICATAT, susunan.saat_dicatat)
  penyalur.langganan(TOPIK_DIPERIKSA, susunan.saat_diperiksa)
  pencatat_audit = audit.PencatatAudit()
  penyalur.langganan(TOPIK_DITERIMA, pencatat_audit.tangani)
  return susunan


if __name__ == "__main__":
  susunan = rakit()
  contoh = domain.buat_permintaan(31, susunan.jumlah_langkah())
  susunan.kirim(contoh)
  contoh.tunggu(BATAS_TUTUP)
  print(contoh.pemberitahuan)
  # Keluarannya: Permintaan 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Pesan lewat antrean: {susunan.pesan_terkirim()}")
  # Keluarannya: Pesan lewat antrean: 4
  susunan.tutup()
