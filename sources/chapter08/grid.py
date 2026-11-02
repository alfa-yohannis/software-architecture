"""Data grid, yaitu copy kuota di memori tiap unit beserta replikasinya.

Setiap processing unit memegang satu DataGrid. Request dilayani dari grid itu,
bukan dari basis data, sehingga pembacaan dan penulisannya tidak menunggu
cakram. Perubahan yang terjadi di satu grid diterbitkan ke saluran replikasi,
lalu diterapkan unit lain sesudah lewat replication lag.

Dua akibat yang diajarkan bab ini lahir di berkas ini. Pertama, selama lag itu
unit lain masih melihat angka lama, dan itulah stale read. Kedua, bila dua unit
mengubah baris yang sama di dalam lag tersebut, satu perubahan menimpa
perubahan yang lain, dan itulah data collision.

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


class PesanReplikasi:
  """Satu perubahan baris kelas yang diterbitkan satu unit kepada unit lain.

  Pesannya membawa versi sebelum perubahan, sehingga penerima dapat mengetahui
  bahwa barisnya sudah berubah sejak pesan itu dibuat. Pengetahuan itulah yang
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
  diterbitkan ke kotak masuk seluruh unit lain, lalu penerimanya menahan pesan
  itu sampai replication lag lewat. Jarak antara penulisan dan penerapannya
  karena itu dapat diatur pada percobaan.

  Kotak masuknya berupa multiprocessing.Queue, bukan daftar biasa, sebab
  processing unit pada skrip pengukuran hasil berjalan sebagai proses
  tersendiri. Satu objek Python hanya hidup di dalam satu proses, sedangkan
  antrean ini membawa pesannya menyeberang.
  """

  def __init__(self, jeda_replikasi: float = JEDA_REPLIKASI_BAKU,
               jumlah_unit: int = JUMLAH_UNIT_BAKU,
               lewat_hub: bool = False) -> None:
    """Menyiapkan satu kotak masuk bagi setiap unit yang akan memakai saluran.

    Seluruh kotak dibuat di muka, sebab antrean antarproses harus sudah ada
    sebelum prosesnya dinyalakan. Jeda disimpan di sini agar seluruh unit
    memakai jeda yang sama, persis seperti satu jaringan yang menghubungkan
    seluruh unit.

    Bila lewat_hub bernilai True, unit hanya menaruh satu pesan ke hub, lalu
    proses replikator yang menyebarkannya ke seluruh kotak masuk. Biaya
    penyebarannya karena itu dibayar prosesor lain, bukan prosesor unitnya.
    """
    self.jeda_replikasi = jeda_replikasi
    self.kotak = [multiprocessing.Queue() for _ in range(jumlah_unit)]
    self.lewat_hub = lewat_hub
    self.hub = multiprocessing.Queue()
    self.cacah_terbit = multiprocessing.Value("i", 0)

  def kotak_unit(self, nomor_unit: int):
    """Menyerahkan kotak masuk milik satu unit, bernomor mulai dari satu.

    Mengembalikan multiprocessing.Queue tempat unit itu menerima pesan unit
    lain. Nomor di luar jangkauan melempar IndexError, sehingga salah hitung
    jumlah unit terlihat seketika.
    """
    return self.kotak[nomor_unit - 1]

  def terbitkan(self, nomor_pengirim: int, pesan: PesanReplikasi) -> None:
    """Menaruh satu pesan perubahan ke kotak masuk seluruh unit lain.

    Pada mode hub, pesannya cukup dititipkan sekali, lalu replikator yang
    menyebarkannya. Tidak mengembalikan apa pun.
    """
    if self.lewat_hub:
      self.hub.put((nomor_pengirim, pesan))
    else:
      self.sebarkan(nomor_pengirim, pesan)
    with self.cacah_terbit.get_lock():
      self.cacah_terbit.value += 1

  def sebarkan(self, nomor_pengirim: int, pesan: PesanReplikasi) -> None:
    """Menyalin satu pesan ke kotak masuk seluruh unit selain pengirimnya.

    Kotak pengirimnya dilewati, sebab perubahannya sudah diterapkan di
    grid-nya sendiri. Tidak mengembalikan apa pun.
    """
    for nomor, kotak in enumerate(self.kotak, start=1):
      if nomor != nomor_pengirim:
        kotak.put(pesan)

  def ambil_dari_hub(self, batas_tunggu: float):
    """Mengambil satu titipan dari hub bagi proses replikator.

    Mengembalikan tuple berisi nomor pengirim dan pesannya, atau None bila hub
    masih kosong sampai batas tunggunya lewat.
    """
    try:
      return self.hub.get(timeout=batas_tunggu)
    except queue.Empty:
      return None

  def jumlah_terbit(self) -> int:
    """Mengembalikan int berisi jumlah perubahan yang sudah diterbitkan."""
    return self.cacah_terbit.value

  def tutup(self) -> None:
    """Membuang pesan yang masih menumpuk di seluruh kotak masuk.

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
  """Copy kuota kelas di memori satu processing unit.

  Pembacaan dijawab dari dict ini tanpa menyentuh cakram. Penulisan mengubah
  dict ini lalu menerbitkan pesan replikasi, sehingga unit yang menjawab
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
    sisa_baru = domain.kurangi_kuota(self.sisa[kode], request)
    self.sisa[kode] = sisa_baru
    self.versi[kode] = versi_sebelum + 1
    self.saluran.terbitkan(self.nomor_unit, PesanReplikasi(
      self.nama_unit, kode, versi_sebelum, sisa_baru, versi_sebelum + 1,
      time.monotonic()))
    return sisa_baru

  def tarik_kotak_masuk(self) -> int:
    """Memindahkan seluruh pesan yang sudah tiba ke daftar pesan tertunda.

    Pesan yang baru tiba belum tentu boleh diterapkan, sebab lag-nya mungkin
    belum lewat. Karena itu pesannya ditahan lebih dahulu di daftar tertunda.
    Mengembalikan int berisi jumlah pesan yang ditarik pada pemanggilan ini.
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
    """Menerapkan pesan unit lain yang sudah melewati replication lag.

    Pesan yang versinya tidak lagi cocok dengan versi baris di grid ini berarti
    kedua unit mengubah baris yang sama di dalam lag, dan kejadian itulah yang
    dicacah sebagai tabrakan. Mengembalikan int berisi jumlah pesan yang
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
    siap.sort(key=operator.attrgetter("waktu"))
    for pesan in siap:
      if self.versi[pesan.kode_kelas] != pesan.versi_sebelum:
        self.jumlah_tabrakan += 1
      self.sisa[pesan.kode_kelas] = pesan.sisa_sesudah
      self.versi[pesan.kode_kelas] = pesan.versi_sesudah
      self.jumlah_terima += 1
    return len(siap)


if __name__ == "__main__":
  saluran_contoh = SaluranReplikasi(jeda_replikasi=0.05, jumlah_unit=2)
  grid_satu = DataGrid("unit-1", saluran_contoh, nomor_unit=1)
  grid_dua = DataGrid("unit-2", saluran_contoh, nomor_unit=2)
  kelas_contoh = sorted(domain.KUOTA_AWAL)[0]
  request_satu = domain.Request(1, "202600001", kelas_contoh)
  request_dua = domain.Request(2, "202600002", kelas_contoh)

  print(f"Sisa awal kedua grid   : {grid_satu.baca(kelas_contoh)}")
  grid_satu.kurangi(request_satu)
  grid_dua.kurangi(request_dua)
  print(f"Sisa unit-1 sesudahnya : {grid_satu.baca(kelas_contoh)}")
  print(f"Sisa unit-2 sesudahnya : {grid_dua.baca(kelas_contoh)}")
  time.sleep(0.06)
  grid_satu.serap_replikasi()
  grid_dua.serap_replikasi()
  print(f"Sisa unit-1 sesudah replikasi: {grid_satu.baca(kelas_contoh)}")
  print(f"Tabrakan tercatat      : "
        f"{grid_satu.jumlah_tabrakan + grid_dua.jumlah_tabrakan}")
  print("Seharusnya dua kuota terjual, sehingga sisanya kurang satu.")
