"""Data grid, yaitu salinan kuota di memori tiap unit beserta replikasinya.

Setiap processing unit memegang satu DataGrid. Request dilayani dari grid itu,
bukan dari basis data, sehingga pembacaan dan penulisannya tidak menunggu
cakram. Perubahan yang terjadi di satu grid diterbitkan ke saluran replikasi,
lalu diterapkan unit lain sesudah lewat replication lag.

Dua akibat yang diajarkan bab ini lahir di file ini. Pertama, selama lag itu
unit lain masih melihat angka lama, dan itulah stale read. Kedua, bila dua unit
mengubah baris yang sama di dalam lag tersebut, satu perubahan menimpa
perubahan yang lain, dan itulah data collision.

Menjalankan file ini memperlihatkan data collision pada kursi terakhir. Dua
unit sama-sama melihat sisa satu, sama-sama menerima mahasiswa, lalu replikasi
saling menimpa sehingga sisanya tercatat nol walaupun dua mahasiswa diterima.

Cara menjalankan: python grid.py
"""

import multiprocessing
import operator
import queue
import time

import domain

# Replication lag bawaan dalam detik. Richards dan Ford memakai 100 milidetik
# sebagai angka pegangan ketika pengukuran nyatanya belum ada.
JEDA_REPLIKASI_BAKU = 0.100
# Jumlah unit bawaan satu saluran, yaitu sepasang unit yang saling mereplikasi.
JUMLAH_UNIT_BAKU = 2
# Replication lag dan kuota tiap kelas pada contoh di bawah, yaitu tinggal satu
# kursi, beserta tambahan waktu tunggu agar lag-nya benar-benar lewat.
JEDA_CONTOH = 0.050
KUOTA_CONTOH = 1
TAMBAHAN_TUNGGU_CONTOH = 0.010


class PesanReplikasi:
  """Satu perubahan baris kelas yang diterbitkan satu unit kepada unit lain.

  Message-nya membawa versi sebelum perubahan, sehingga penerima dapat mengetahui
  bahwa barisnya sudah berubah sejak message itu dibuat. Pengetahuan itulah yang
  dipakai untuk mencacah tabrakan.
  """

  def __init__(self, pengirim: str, kode_kelas: str, versi_sebelum: int,
               sisa_sesudah: int, versi_sesudah: int, waktu: float) -> None:
    """Menyimpan isi perubahan beserta waktu terbitnya.

    Waktu terbit dipakai penerima untuk menunda penerapan selama replication
    lag, sehingga penundaannya terukur, bukan ditaksir.
    """
    self.pengirim = pengirim
    self.kode_kelas = kode_kelas
    self.versi_sebelum = versi_sebelum
    self.sisa_sesudah = sisa_sesudah
    self.versi_sesudah = versi_sesudah
    self.waktu = waktu


class SaluranReplikasi:
  """Saluran replikasi yang memberi tiap unit satu kotak masuk sendiri.

  Saluran ini meniru data grid pada virtualized middleware. Satu perubahan
  diterbitkan ke kotak masuk seluruh unit lain, lalu penerimanya menahan message
  itu sampai replication lag lewat. Jarak antara penulisan dan penerapannya
  karena itu dapat diatur pada percobaan.

  Kotak masuknya berupa multiprocessing.Queue, bukan daftar biasa, sebab
  processing unit pada skrip pengukuran hasil berjalan sebagai proses
  tersendiri. Satu objek Python hanya hidup di dalam satu proses, sedangkan
  antrean ini membawa message-nya menyeberang.
  """

  def __init__(self, jeda_replikasi: float = JEDA_REPLIKASI_BAKU,
               jumlah_unit: int = JUMLAH_UNIT_BAKU,
               lewat_hub: bool = False) -> None:
    """Menyiapkan satu kotak masuk bagi setiap unit yang akan memakai saluran.

    Seluruh kotak dibuat di muka, sebab antrean antarproses harus sudah ada
    sebelum prosesnya dinyalakan. Jeda disimpan di sini agar seluruh unit
    memakai jeda yang sama, persis seperti satu jaringan yang menghubungkan
    seluruh unit.

    Bila lewat_hub bernilai True, unit hanya menaruh satu message ke hub, lalu
    proses replikator yang menyebarkannya ke seluruh kotak masuk. Biaya
    penyebarannya karena itu dibayar prosesor lain, bukan prosesor unitnya.
    """
    self.jeda_replikasi = jeda_replikasi
    self.kotak = [multiprocessing.Queue() for _ in range(jumlah_unit)]
    self.lewat_hub = lewat_hub
    self.hub = multiprocessing.Queue()

  def kotak_unit(self, nomor_unit: int):
    """Menyerahkan kotak masuk milik satu unit, bernomor mulai dari satu.

    Mengembalikan multiprocessing.Queue tempat unit itu menerima message unit
    lain. Nomor di luar jangkauan melempar IndexError, sehingga salah hitung
    jumlah unit terlihat seketika.
    """
    return self.kotak[nomor_unit - 1]

  def terbitkan(self, nomor_pengirim: int, pesan: PesanReplikasi) -> None:
    """Menaruh satu message perubahan ke kotak masuk seluruh unit lain.

    Pada mode hub, message-nya cukup dititipkan sekali, lalu replikator yang
    menyebarkannya. Tidak mengembalikan apa pun.
    """
    if self.lewat_hub:
      self.hub.put((nomor_pengirim, pesan))
    else:
      self.sebarkan(nomor_pengirim, pesan)

  def sebarkan(self, nomor_pengirim: int, pesan: PesanReplikasi) -> None:
    """Menyalin satu message ke kotak masuk seluruh unit selain pengirimnya.

    Kotak pengirimnya dilewati, sebab perubahannya sudah diterapkan di
    grid-nya sendiri. Pada N unit, satu perubahan karena itu menjadi N - 1
    kali penulisan ke antrean. Tidak mengembalikan apa pun.
    """
    for nomor, kotak in enumerate(self.kotak, start=1):
      if nomor != nomor_pengirim:
        kotak.put(pesan)

  def ambil_dari_hub(self, batas_tunggu: float):
    """Mengambil satu titipan dari hub bagi proses replikator.

    Mengembalikan tuple berisi nomor pengirim dan message-nya, atau None bila hub
    masih kosong sampai batas tunggunya lewat.
    """
    try:
      return self.hub.get(timeout=batas_tunggu)
    except queue.Empty:
      return None

  def lepas_tanpa_menunggu(self) -> None:
    """Membiarkan proses pemanggil berakhir tanpa menunggu kotak masuk terbaca.

    Unit yang sudah menerima tanda berhenti tidak membaca kotak masuknya lagi,
    sehingga pipa antrean itu dapat penuh. Proses lain yang masih menitipkan
    message ke sana lalu tertahan selamanya ketika hendak berakhir, sebab
    antrean antarproses menunggu seluruh isinya terkirim lebih dahulu. Message
    replikasi yang tersisa sesudah beban selesai tidak dibutuhkan lagi, sehingga
    setiap proses unit dan replikator memanggil ini sebelum berakhir.

    Hub sengaja tidak dilepas. Isinya masih dibaca replikator sampai penanda
    berhenti tiba, sehingga pipanya tidak akan penuh. Melepasnya justru
    berbahaya, sebab proses yang berakhir di tengah penulisan meninggalkan
    kunci tulis hub dalam keadaan terkunci, lalu penanda berhenti dari proses
    utama tidak pernah sampai. Tidak mengembalikan apa pun.
    """
    for kotak in self.kotak:
      kotak.cancel_join_thread()

  def tutup(self) -> None:
    """Membuang message yang masih menumpuk di seluruh kotak masuk.

    Unit yang sudah mati tidak pernah membaca kotaknya lagi, sedangkan antrean
    antarproses menahan proses pemiliknya selama isinya belum terbaca. Tanpa
    pemanggilan ini, percobaan yang mematikan unit di tengah jalan akan
    menggantung saat hendak berakhir. Tidak mengembalikan apa pun.
    """
    for kotak in self.kotak:
      kotak.cancel_join_thread()
      kotak.close()
    self.hub.cancel_join_thread()
    self.hub.close()


class DataGrid:
  """Salinan kuota kelas di memori satu processing unit.

  Pembacaan dijawab dari dict ini tanpa menyentuh cakram. Penulisan mengubah
  dict ini lalu menerbitkan message replikasi, sehingga unit yang menjawab
  request tidak pernah menunggu unit lain.
  """

  def __init__(self, nama_unit: str, saluran: SaluranReplikasi,
               per_kelas: int = None, nomor_unit: int = 1) -> None:
    """Mengisi grid dengan kuota awal lalu mengambil kotak masuk salurannya.

    Pengisian awal meniru data reader yang memuat grid ketika unit menyala.
    Argumen per_kelas menaikkan kuota seluruh kelas, dipakai skrip pengukuran
    hasil agar request tidak habis ditolak sebelum sempat dikerjakan. Argumen
    nomor_unit menentukan kotak masuk mana yang menjadi milik grid ini.
    """
    self.nama_unit = nama_unit
    self.nomor_unit = nomor_unit
    self.saluran = saluran
    self.kotak = saluran.kotak_unit(nomor_unit)
    self.sisa = domain.kuota_awal(per_kelas)
    self.versi = {kode: domain.VERSI_AWAL for kode in self.sisa}
    self.tertunda = []
    self.jumlah_tabrakan = 0
    self.jumlah_terima = 0

  def baca(self, kode_kelas: str) -> int:
    """Membaca sisa kuota dari memori unit ini sendiri.

    Angkanya boleh tertinggal dari unit lain selama replication lag belum
    lewat. Mengembalikan int berisi sisa kuota menurut grid ini.
    """
    return self.sisa[kode_kelas]

  def kurangi(self, request: domain.Request) -> int:
    """Mengurangi satu kuota di grid ini lalu menerbitkan perubahannya.

    Melempar KuotaHabis bila kuotanya sudah nol menurut grid ini. Mengembalikan
    int berisi sisa kuota sesudah pengurangan.
    """
    kode = request.kode_kelas
    versi_sebelum = self.versi[kode]
    versi_sesudah = versi_sebelum + 1
    sisa_baru = domain.kurangi_kuota(self.sisa[kode], request)
    self.sisa[kode] = sisa_baru
    self.versi[kode] = versi_sesudah
    waktu_terbit = time.monotonic()
    pesan = PesanReplikasi(self.nama_unit, kode, versi_sebelum, sisa_baru,
                           versi_sesudah, waktu_terbit)
    self.saluran.terbitkan(self.nomor_unit, pesan)
    return sisa_baru

  def tarik_kotak_masuk(self) -> int:
    """Memindahkan seluruh message yang sudah tiba ke daftar message tertunda.

    Message yang baru tiba belum tentu boleh diterapkan, sebab lag-nya mungkin
    belum lewat. Karena itu message-nya ditahan lebih dahulu di daftar tertunda.
    Mengembalikan int berisi jumlah message yang ditarik pada pemanggilan ini.
    """
    jumlah = 0
    while True:
      try:
        pesan = self.kotak.get_nowait()
      except queue.Empty:
        return jumlah
      self.tertunda.append(pesan)
      jumlah += 1

  def serap_replikasi(self) -> int:
    """Menerapkan message unit lain yang sudah melewati replication lag.

    Message yang versinya tidak lagi cocok dengan versi baris di grid ini berarti
    kedua unit mengubah baris yang sama di dalam lag, dan kejadian itulah yang
    dicacah sebagai tabrakan. Mengembalikan int berisi jumlah message yang
    diterapkan pada pemanggilan ini.
    """
    self.tarik_kotak_masuk()
    sekarang = time.monotonic()
    siap = []
    masih_ditahan = []
    for pesan in self.tertunda:
      if sekarang - pesan.waktu >= self.saluran.jeda_replikasi:
        siap.append(pesan)
      else:
        masih_ditahan.append(pesan)
    self.tertunda = masih_ditahan
    urut_waktu = operator.attrgetter("waktu")
    siap.sort(key=urut_waktu)
    for pesan in siap:
      if self.versi[pesan.kode_kelas] != pesan.versi_sebelum:
        self.jumlah_tabrakan += 1
      self.sisa[pesan.kode_kelas] = pesan.sisa_sesudah
      self.versi[pesan.kode_kelas] = pesan.versi_sesudah
      self.jumlah_terima += 1
    return len(siap)


if __name__ == "__main__":
  saluran_contoh = SaluranReplikasi(JEDA_CONTOH, jumlah_unit=2)
  grid_satu = DataGrid("unit-1", saluran_contoh, KUOTA_CONTOH, 1)
  grid_dua = DataGrid("unit-2", saluran_contoh, KUOTA_CONTOH, 2)
  kelas_contoh = sorted(domain.KUOTA_AWAL)[0]
  request_satu = domain.Request(1, "202600001", kelas_contoh)
  request_dua = domain.Request(2, "202600002", kelas_contoh)

  print(f"Sisa {kelas_contoh} di kedua grid : "
        f"{grid_satu.baca(kelas_contoh)}")
  diterima = 0
  for grid_unit, request_contoh in ((grid_satu, request_satu),
                                    (grid_dua, request_dua)):
    sisa_baru = grid_unit.kurangi(request_contoh)
    diterima += 1
    print(f"{grid_unit.nama_unit} menerima {request_contoh.nim}, "
          f"sisa menjadi {sisa_baru}")
  time.sleep(JEDA_CONTOH + TAMBAHAN_TUNGGU_CONTOH)
  grid_satu.serap_replikasi()
  grid_dua.serap_replikasi()
  print(f"Sisa sesudah replikasi : {grid_satu.baca(kelas_contoh)} di unit-1, "
        f"{grid_dua.baca(kelas_contoh)} di unit-2")
  print(f"Mahasiswa diterima     : {diterima} untuk {KUOTA_CONTOH} kuota")
  print(f"Tabrakan tercatat      : "
        f"{grid_satu.jumlah_tabrakan + grid_dua.jumlah_tabrakan}")
  saluran_contoh.tutup()
  # Keluarannya baris terakhir: Tabrakan tercatat      : 2
