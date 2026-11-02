"""Data pump beserta data writer, yaitu jalan menuju basis data.

Processing unit tidak pernah menyentuh basis data. Perubahan yang sudah
dijawab kepada mahasiswa dititipkan ke data pump, yaitu antrean yang menjaga
urutan kirim. Data writer mengambilnya dari antrean itu lalu menuliskannya ke
basis data sekelompok sekaligus.

Pengelompokan itulah yang membuat penulisan jauh lebih murah daripada satu
commit per request. Harganya juga jelas, yaitu kiriman yang masih menunggu di
antrean akan lenyap bila unitnya mati lebih dahulu, dan kehilangan itu diukur
pada uji_kehilangan.py.

Cara menjalankan: python pompa.py
"""

import multiprocessing
import queue
import threading

import basis_data

# Banyaknya kiriman yang dikumpulkan sebelum satu commit dijalankan.
UKURAN_KELOMPOK = 50
# Lama menunggu kiriman berikutnya sebelum kelompok yang belum penuh dikirim.
JEDA_KIRIM = 0.05


class KirimanPerubahan:
  """Satu perubahan yang harus sampai ke basis data, beserta pengambilannya.

  Isinya sengaja lengkap, yaitu sisa kuota terbaru sekaligus baris pengambilan
  mahasiswanya, sehingga data writer tidak perlu menanyakan apa pun kepada
  unit pengirimnya.
  """

  def __init__(self, nomor: int, nim: str, kode_kelas: str, sisa: int,
               unit: str) -> None:
    """Menyimpan isi satu kiriman apa adanya, tanpa menghitung ulang."""
    self.nomor = nomor
    self.nim = nim
    self.kode_kelas = kode_kelas
    self.sisa = sisa
    self.unit = unit


class DataPump:
  """Antrean kiriman dari seluruh unit menuju data writer.

  Urutannya dijaga, yaitu kiriman yang lebih dahulu masuk lebih dahulu pula
  ditulis. Antrean ini berada di luar jalur request, sehingga unit yang
  mengirim tidak pernah menunggu basis data.

  Antreannya multiprocessing.Queue, sebab pengirimnya adalah processing unit
  yang berjalan sebagai proses tersendiri, sedangkan pembacanya satu data
  writer di proses pemanggil.
  """

  def __init__(self) -> None:
    """Menyiapkan antrean kiriman beserta pencacah kedalamannya."""
    self.antrean = multiprocessing.Queue()
    self.cacah_kirim = multiprocessing.Value("i", 0)
    self.cacah_terdalam = multiprocessing.Value("i", 0)

  def kirim(self, kiriman: KirimanPerubahan) -> None:
    """Menitipkan satu perubahan untuk ditulis belakangan.

    Tidak mengembalikan apa pun.
    """
    self.antrean.put(kiriman)
    with self.cacah_kirim.get_lock():
      self.cacah_kirim.value += 1
    panjang = self.antrean.qsize()
    with self.cacah_terdalam.get_lock():
      if panjang > self.cacah_terdalam.value:
        self.cacah_terdalam.value = panjang

  def ambil(self, batas_tunggu: float):
    """Mengambil satu kiriman bagi data writer.

    Mengembalikan KirimanPerubahan bila ada, atau None bila antreannya kosong
    sampai batas tunggunya lewat.
    """
    try:
      return self.antrean.get(timeout=batas_tunggu)
    except queue.Empty:
      return None

  def tertahan(self) -> int:
    """Mengembalikan int berisi jumlah kiriman yang belum ditulis."""
    return self.antrean.qsize()

  def jumlah_terkirim(self) -> int:
    """Mengembalikan int berisi jumlah kiriman yang pernah masuk antrean."""
    return self.cacah_kirim.value

  def kedalaman_terdalam(self) -> int:
    """Mengembalikan int berisi antrean terpanjang yang pernah tercatat."""
    return self.cacah_terdalam.value


class DataWriter:
  """Pengambil kiriman dari data pump yang menuliskannya ke basis data.

  Penulisannya dikelompokkan, yaitu beberapa kiriman ditulis lalu ditutup satu
  commit. Thread ini satu-satunya pihak yang memegang koneksi basis data pada
  versi space.
  """

  def __init__(self, pump: DataPump, jalur_basis: str,
               ukuran_kelompok: int = UKURAN_KELOMPOK) -> None:
    """Menyimpan sumber kiriman beserta berkas basis data tujuannya."""
    self.pump = pump
    self.jalur_basis = jalur_basis
    self.ukuran_kelompok = ukuran_kelompok
    self.berhenti = threading.Event()
    self.utas = None
    self.jumlah_tulis = 0
    self.jumlah_commit = 0

  def mulai(self) -> None:
    """Menjalankan penulisan pada thread tersendiri.

    Tidak mengembalikan apa pun.
    """
    self.utas = threading.Thread(target=self.layani, daemon=True)
    self.utas.start()

  def layani(self) -> None:
    """Mengambil kiriman terus-menerus lalu menuliskannya sekelompok.

    Tidak mengembalikan apa pun.
    """
    basis = basis_data.BasisData(self.jalur_basis)
    kelompok = []
    while not self.berhenti.is_set() or self.pump.tertahan() > 0:
      kiriman = self.pump.ambil(JEDA_KIRIM)
      if kiriman is not None:
        kelompok.append(kiriman)
      penuh = len(kelompok) >= self.ukuran_kelompok
      sepi = kiriman is None and kelompok
      if penuh or sepi:
        self.tulis_kelompok(basis, kelompok)
        kelompok = []
    if kelompok:
      self.tulis_kelompok(basis, kelompok)
    basis.tutup()

  def tulis_kelompok(self, basis: basis_data.BasisData, kelompok: list) -> None:
    """Menuliskan satu kelompok kiriman lalu menutupnya dengan satu commit.

    Tidak mengembalikan apa pun.
    """
    for kiriman in kelompok:
      basis.tulis_sisa(kiriman.kode_kelas, kiriman.sisa)
      basis.catat_pengambilan(kiriman.nomor, kiriman.nim, kiriman.kode_kelas,
                              kiriman.unit)
    basis.simpan()
    self.jumlah_tulis += len(kelompok)
    self.jumlah_commit += 1

  def hentikan(self) -> None:
    """Menghentikan penulisan sesudah antreannya habis."""
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=5.0)


if __name__ == "__main__":
  import domain

  basis_data.siapkan_berkas_baru()
  pump_contoh = DataPump()
  writer_contoh = DataWriter(pump_contoh, basis_data.NAMA_BERKAS,
                             ukuran_kelompok=10)
  writer_contoh.mulai()
  sisa_contoh = domain.kuota_awal()
  for request_contoh in domain.bangkitkan_request(25):
    sisa_contoh[request_contoh.kode_kelas] -= 1
    pump_contoh.kirim(KirimanPerubahan(
      request_contoh.nomor, request_contoh.nim, request_contoh.kode_kelas,
      sisa_contoh[request_contoh.kode_kelas], "unit-1"))
  print(f"Kiriman masuk pump   : {pump_contoh.jumlah_terkirim()}")
  print(f"Antrean terdalam     : {pump_contoh.kedalaman_terdalam()}")
  writer_contoh.hentikan()
  basis_periksa = basis_data.BasisData()
  print(f"Baris tersimpan      : {basis_periksa.jumlah_pengambilan()}")
  print(f"Commit dijalankan    : {writer_contoh.jumlah_commit}")
  basis_periksa.tutup()
