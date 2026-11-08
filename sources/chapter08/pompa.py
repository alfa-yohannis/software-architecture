"""Data pump beserta data writer, yaitu jalan menuju basis data.

Processing unit tidak pernah menyentuh basis data. Perubahan yang sudah
dijawab kepada mahasiswa dititipkan ke data pump, yaitu antrean yang menjaga
urutan kirim. Satu kiriman berisi sekelompok perubahan, sebanyak isi penyangga
unit pengirimnya. Data writer mengambil kiriman itu lalu menuliskannya ke
basis data sekelompok sekaligus.

Pengelompokan itulah yang membuat penulisan jauh lebih murah daripada satu
commit per request. Harganya juga jelas, yaitu perubahan yang masih tertahan
di penyangga unit akan lenyap bila unitnya mati lebih dahulu, dan kehilangan
itu diukur pada uji_kehilangan.py.

Cara menjalankan: python pompa.py
"""

import multiprocessing
import queue
import threading

import basis_data

# Banyaknya perubahan yang dikumpulkan data writer sebelum satu commit.
UKURAN_KELOMPOK = 50
# Lama data writer menunggu kiriman berikutnya. Bila tidak ada yang datang
# selama itu, kelompok yang belum penuh tetap ditulis, sehingga perubahan tidak
# tertahan di data writer ketika beban sepi.
JEDA_KIRIM = 0.05
# Penanda yang disisipkan ke data pump ketika data writer diminta berhenti.
# Bentuknya teks, sebab objek yang menyeberang antrean antarproses disalin,
# sehingga hanya nilainya yang dapat dibandingkan.
PENANDA_SELESAI = "selesai"
# Banyaknya perubahan dan ukuran penyangga pada contoh di bawah.
JUMLAH_CONTOH = 25
PENYANGGA_CONTOH = 10


class Perubahan:
  """Satu perubahan kuota yang harus sampai ke basis data.

  Isinya sengaja lengkap, yaitu sisa kuota terbaru sekaligus baris pengambilan
  mahasiswanya, sehingga data writer tidak perlu menanyakan apa pun kepada
  unit pengirimnya.
  """

  def __init__(self, nomor: int, nim: str, kode_kelas: str, sisa: int,
               unit: str) -> None:
    """Menyimpan isi perubahan apa adanya, tanpa menghitung ulang.

    Sisa kuota diterima dalam bentuk akhirnya, sebab aturan bisnisnya sudah
    diperiksa unit pengirim ketika request dilayani.
    """
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
    """Menyiapkan antrean kiriman sebelum proses unit dinyalakan.

    Antrean antarproses harus sudah ada sebelum prosesnya dibuat, sebab
    antrean itu diwariskan lewat argumen proses, bukan dicari belakangan.
    """
    self.antrean = multiprocessing.Queue()

  def kirim(self, kelompok: list) -> None:
    """Menitipkan sekelompok perubahan sebagai satu kiriman.

    Satu kiriman berarti satu kali pengemasan dan satu kali penulisan ke pipa
    antarproses, berapa pun isinya. Karena itu kiriman berisi lima puluh
    perubahan jauh lebih murah daripada lima puluh kiriman berisi satu
    perubahan. Tidak mengembalikan apa pun.
    """
    self.antrean.put(kelompok)

  def kirim_penanda_selesai(self) -> None:
    """Menaruh penanda selesai di belakang seluruh kiriman yang sudah ada.

    Dipakai data writer ketika diminta berhenti. Penanda itu masuk paling
    belakang, sehingga kiriman yang lebih dahulu masuk tetap ditulis lebih
    dahulu. Tidak mengembalikan apa pun.
    """
    self.antrean.put(PENANDA_SELESAI)

  def ambil(self, batas_tunggu: float):
    """Mengambil satu kiriman bagi data writer.

    Mengembalikan list berisi Perubahan, teks PENANDA_SELESAI, atau None bila
    antreannya kosong sampai batas tunggunya lewat.
    """
    try:
      return self.antrean.get(timeout=batas_tunggu)
    except queue.Empty:
      return None


class DataWriter:
  """Pengambil kiriman dari data pump yang menuliskannya ke basis data.

  Penulisannya dikelompokkan, yaitu beberapa perubahan ditulis lalu ditutup
  satu commit. Thread ini satu-satunya pihak yang memegang koneksi basis data
  pada versi space.
  """

  def __init__(self, pump: DataPump, jalur_basis: str,
               ukuran_kelompok: int = UKURAN_KELOMPOK) -> None:
    """Menyimpan sumber kiriman, file basis data tujuan, dan ukuran kelompok.

    Pencacahnya dipegang di sini, bukan di data pump, sebab data writer hanya
    satu sedangkan pengirimnya banyak proses. Pencacah di sisi pembaca tidak
    menambah satu pun pekerjaan bagi processing unit.
    """
    self.pump = pump
    self.jalur_basis = jalur_basis
    self.ukuran_kelompok = ukuran_kelompok
    self.utas = None
    self.jumlah_kiriman = 0
    self.jumlah_tulis = 0
    self.jumlah_commit = 0

  def mulai(self) -> None:
    """Menjalankan penulisan pada thread tersendiri di proses pemanggil.

    Thread dipakai, bukan proses, sebab penulisnya hanya satu dan sebagian
    besar waktunya menunggu cakram. Tidak mengembalikan apa pun.
    """
    self.utas = threading.Thread(target=self.layani, daemon=True)
    self.utas.start()

  def layani(self) -> None:
    """Mengambil kiriman terus-menerus lalu menuliskannya sekelompok.

    Kelompok ditulis ketika sudah berisi ukuran_kelompok perubahan, ketika
    tidak ada kiriman selama JEDA_KIRIM, atau ketika penanda selesai tiba.
    Tidak mengembalikan apa pun.
    """
    basis = basis_data.BasisData(self.jalur_basis)
    kelompok = []
    while True:
      kiriman = self.pump.ambil(JEDA_KIRIM)
      if kiriman == PENANDA_SELESAI:
        break
      if kiriman is not None:
        self.jumlah_kiriman += 1
        kelompok.extend(kiriman)
      penuh = len(kelompok) >= self.ukuran_kelompok
      sepi = kiriman is None and kelompok
      if penuh or sepi:
        self.tulis_kelompok(basis, kelompok)
        kelompok = []
    if kelompok:
      self.tulis_kelompok(basis, kelompok)
    basis.tutup()

  def tulis_kelompok(self, basis: basis_data.BasisData, kelompok: list) -> None:
    """Menuliskan satu kelompok perubahan lalu menutupnya dengan satu commit.

    Tidak mengembalikan apa pun.
    """
    for perubahan in kelompok:
      basis.tulis_sisa(perubahan.kode_kelas, perubahan.sisa)
      basis.catat_pengambilan(perubahan.nomor, perubahan.nim,
                              perubahan.kode_kelas, perubahan.unit)
    basis.simpan()
    self.jumlah_tulis += len(kelompok)
    self.jumlah_commit += 1

  def hentikan(self) -> None:
    """Menghentikan penulisan sesudah seluruh kiriman yang sudah ada ditulis.

    Penanda selesai membangunkan data writer seketika, sehingga lama menyimpan
    tidak bertambah satu JEDA_KIRIM hanya karena data writer sedang menunggu
    kiriman yang tidak akan datang lagi. Tidak mengembalikan apa pun.
    """
    self.pump.kirim_penanda_selesai()
    if self.utas is not None:
      self.utas.join(timeout=5.0)


if __name__ == "__main__":
  import domain

  basis_data.siapkan_berkas_baru()
  pump_contoh = DataPump()
  writer_contoh = DataWriter(pump_contoh, basis_data.NAMA_BERKAS)
  writer_contoh.mulai()
  sisa_contoh = domain.kuota_awal()
  penyangga = []
  for request_contoh in domain.bangkitkan_request(JUMLAH_CONTOH):
    kode = request_contoh.kode_kelas
    sisa_contoh[kode] -= 1
    perubahan_contoh = Perubahan(request_contoh.nomor, request_contoh.nim,
                                 kode, sisa_contoh[kode], "unit-1")
    penyangga.append(perubahan_contoh)
    if len(penyangga) >= PENYANGGA_CONTOH:
      pump_contoh.kirim(penyangga)
      penyangga = []
  if penyangga:
    pump_contoh.kirim(penyangga)
  writer_contoh.hentikan()
  basis_periksa = basis_data.BasisData()
  print(f"Perubahan dikirim    : {JUMLAH_CONTOH}")
  print(f"Kiriman ke data pump : {writer_contoh.jumlah_kiriman}")
  print(f"Baris tersimpan      : {basis_periksa.jumlah_pengambilan()}")
  print(f"Commit dijalankan    : {writer_contoh.jumlah_commit}")
  basis_periksa.tutup()
  # Keluarannya baris terakhir: Commit dijalankan    : 1
