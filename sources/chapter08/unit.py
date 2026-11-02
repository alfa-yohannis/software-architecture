"""Processing unit kedua versi, yaitu versi space dan versi basis data.

Versi space melayani request dari grid memorinya sendiri, lalu menitipkan
perubahannya kepada data pump. Versi basis data membuka satu transaksi ke
basis data untuk setiap request. Keduanya memakai aturan bisnis yang sama dari
domain.py, sehingga selisih hasil pengukurannya benar-benar berasal dari cara
menyimpan, bukan dari cara menghitung.

Menjalankan berkas ini mencetak jejak satu request langkah demi langkah, mulai
dari mahasiswa menekan simpan sampai barisnya tersimpan di basis data.

Cara menjalankan: python unit.py
"""

import threading
import time

import basis_data
import domain
import grid as modul_grid
import middleware as modul_middleware
import pompa as modul_pompa

MILIDETIK = 1000.0
# Lama unit menunggu request berikutnya sebelum memeriksa tanda berhenti.
BATAS_TUNGGU_REQUEST = 0.05
# Nomor request penanda berhenti. Satu penanda dikirim untuk setiap unit,
# sehingga tiap unit mengambil tepat satu lalu keluar dari perulangannya.
NOMOR_BERHENTI = -1
# Banyaknya perubahan yang ditahan di memori unit sebelum diserahkan kepada
# data pump. Nilai satu berarti setiap perubahan langsung diserahkan, sehingga
# tidak ada yang tertahan. Nilai yang lebih besar membuat penyerahannya lebih
# murah, tetapi perubahan yang masih tertahan akan lenyap bila unitnya mati.
UKURAN_PENYANGGA_BAKU = 1


class ProcessingUnit:
  """Unit versi space yang memegang grid sendiri dan tidak menyentuh cakram.

  Satu unit melayani satu request pada satu waktu. Seluruh jawabannya diambil
  dari grid memorinya, sehingga mahasiswa menerima jawaban tanpa menunggu
  basis data maupun unit lain.
  """

  def __init__(self, nama: str, messaging_grid, saluran, pump,
               per_kelas: int = None,
               ukuran_penyangga: int = UKURAN_PENYANGGA_BAKU,
               nomor_unit: int = 1) -> None:
    """Merangkai unit dengan messaging grid, data grid, dan data pump.

    Grid-nya diisi kuota awal saat objek dibuat, dan pengisian itu meniru data
    reader yang memuat cache ketika unit menyala. Nomor unit menentukan kotak
    masuk replikasi mana yang menjadi milik grid ini.
    """
    self.nama = nama
    self.messaging_grid = messaging_grid
    self.grid = modul_grid.DataGrid(nama, saluran, per_kelas, nomor_unit)
    self.pump = pump
    self.jumlah_dilayani = 0
    self.jumlah_ditolak = 0
    self.lama_layan = []
    self.ukuran_penyangga = ukuran_penyangga
    self.penyangga = []
    self.berhenti = threading.Event()
    self.utas = None

  def layani(self, request: domain.Request) -> domain.Jawaban:
    """Melayani satu request sepenuhnya dari memori unit ini.

    Urutannya tetap, yaitu menyerap replikasi yang sudah matang, membaca sisa
    kuota dari grid, menjalankan aturan bisnis, lalu menitipkan perubahannya
    kepada data pump. Request yang hanya membaca berhenti pada langkah kedua,
    sehingga tidak menitipkan apa pun dan tidak mengabarkan apa pun.
    Mengembalikan Jawaban berisi hasil beserta sisa kuota yang terlihat unit
    ini.
    """
    self.grid.serap_replikasi()
    if request.jenis == domain.JENIS_BACA:
      self.jumlah_dilayani += 1
      return domain.Jawaban(request.nomor, True,
                            self.grid.baca(request.kode_kelas), "sisa dibaca")
    try:
      sisa_baru = self.grid.kurangi(request)
    except domain.KuotaHabis as galat:
      self.jumlah_ditolak += 1
      return domain.Jawaban(request.nomor, False, 0, str(galat))
    self.penyangga.append(modul_pompa.KirimanPerubahan(
      request.nomor, request.nim, request.kode_kelas, sisa_baru, self.nama))
    if len(self.penyangga) >= self.ukuran_penyangga:
      self.serahkan_penyangga()
    self.jumlah_dilayani += 1
    return domain.Jawaban(request.nomor, True, sisa_baru, "diterima")

  def serahkan_penyangga(self) -> int:
    """Menyerahkan seluruh isi penyangga kepada data pump lalu mengosongkannya.

    Mengembalikan int berisi jumlah perubahan yang diserahkan.
    """
    jumlah = len(self.penyangga)
    for kiriman in self.penyangga:
      self.pump.kirim(kiriman)
    self.penyangga = []
    return jumlah

  def mati(self) -> int:
    """Mematikan unit ini seketika, sehingga isi penyangganya ikut lenyap.

    Dipakai uji_kehilangan.py untuk meniru mesin yang padam di tengah beban.
    Mengembalikan int berisi jumlah perubahan yang lenyap bersama unit ini.
    """
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=2.0)
    hilang = len(self.penyangga)
    self.penyangga = []
    return hilang

  def jalankan(self) -> None:
    """Mengambil request dari messaging grid sampai tanda berhenti menyala.

    Tidak mengembalikan apa pun.
    """
    while not self.berhenti.is_set():
      request = self.messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
      if request is None:
        self.grid.serap_replikasi()
        continue
      mulai = time.monotonic()
      self.layani(request)
      self.lama_layan.append((time.monotonic() - mulai) * MILIDETIK)

  def mulai(self) -> None:
    """Menjalankan unit ini pada thread tersendiri."""
    self.utas = threading.Thread(target=self.jalankan, daemon=True)
    self.utas.start()

  def hentikan(self) -> None:
    """Menghentikan unit ini sesudah penyangganya diserahkan lebih dahulu."""
    self.serahkan_penyangga()
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=2.0)


class UnitBasisData:
  """Unit pembanding yang membuka transaksi basis data pada setiap request.

  Aturan bisnisnya sama persis, dan yang berbeda hanya tempat kuotanya dibaca
  serta ditulis. Setiap request karena itu menunggu giliran menulis ke berkas
  yang sama.
  """

  def __init__(self, nama: str, messaging_grid, jalur_basis: str) -> None:
    """Menyimpan nama unit beserta berkas basis data yang dipakainya."""
    self.nama = nama
    self.messaging_grid = messaging_grid
    self.jalur_basis = jalur_basis
    self.jumlah_dilayani = 0
    self.jumlah_ditolak = 0
    self.lama_layan = []
    self.berhenti = threading.Event()
    self.utas = None

  def jalankan(self) -> None:
    """Melayani request sampai tanda berhenti menyala, satu koneksi per unit.

    Tidak mengembalikan apa pun.
    """
    basis = basis_data.BasisData(self.jalur_basis)
    while not self.berhenti.is_set():
      request = self.messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
      if request is None:
        continue
      mulai = time.monotonic()
      jawaban = basis.layani(request, self.nama)
      self.lama_layan.append((time.monotonic() - mulai) * MILIDETIK)
      if jawaban.diterima:
        self.jumlah_dilayani += 1
      else:
        self.jumlah_ditolak += 1
    basis.tutup()

  def mulai(self) -> None:
    """Menjalankan unit ini pada thread tersendiri."""
    self.utas = threading.Thread(target=self.jalankan, daemon=True)
    self.utas.start()

  def mati(self) -> int:
    """Mematikan unit ini seketika, sebagai pembanding bagi versi space.

    Tidak ada perubahan yang tertahan di memori unit ini, sebab setiap request
    sudah tertulis sebelum mahasiswanya dijawab. Mengembalikan int bernilai
    nol, yaitu jumlah perubahan yang lenyap bersama unit ini.
    """
    self.hentikan()
    return 0

  def hentikan(self) -> None:
    """Menghentikan unit ini lalu menunggu threadnya selesai."""
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=5.0)


def jalankan_unit_space_proses(nama: str, nomor_unit: int, messaging_grid,
                               saluran, pump, pencatat, gerbang,
                               per_kelas: int, ukuran_penyangga: int,
                               inti: int = None) -> None:
  """Menjalankan satu processing unit versi space sebagai proses tersendiri.

  Seluruh bagian bersama diterima sebagai argumen, yaitu antrean request,
  saluran replikasi, data pump, dan pencatat. Semuanya dibuat pemanggil
  sebelum proses dinyalakan, sebab antrean antarproses tidak dapat dikirim
  sesudahnya.

  Gerbang menahan unit sampai seluruh unit lain selesai menyala, sehingga lama
  penyalaan proses tidak ikut terhitung sebagai lama melayani. Argumen inti
  mengunci unit ini pada satu prosesor. Unit kemudian melayani request sampai
  menerima tanda berhenti, lalu menitipkan hasil hitungannya ke pencatat.
  Tidak mengembalikan apa pun.
  """
  modul_middleware.kunci_ke_inti(inti)
  unit = ProcessingUnit(nama, messaging_grid, saluran, pump, per_kelas,
                        ukuran_penyangga, nomor_unit)
  gerbang.wait()
  while True:
    request = messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
    if request is None:
      continue
    if request.nomor == NOMOR_BERHENTI:
      break
    unit.layani(request)
    unit.lama_layan.append((time.monotonic() - request.waktu_kirim)
                           * MILIDETIK)
  unit.serahkan_penyangga()
  pencatat.catat(nama, unit.jumlah_dilayani, unit.jumlah_ditolak,
                 unit.lama_layan, time.monotonic())


def jalankan_unit_basis_data_proses(nama: str, messaging_grid, pencatat,
                                    gerbang, jalur_basis: str,
                                    inti: int = None) -> None:
  """Menjalankan satu unit versi basis data sebagai proses tersendiri.

  Setiap proses membuka koneksinya sendiri, sehingga perebutan giliran menulis
  benar-benar terjadi antar proses. Gerbangnya sama dengan versi space, yaitu
  menahan unit sampai seluruh unit siap, dan penguncian intinya pun sama.
  Tidak mengembalikan apa pun.
  """
  modul_middleware.kunci_ke_inti(inti)
  basis = basis_data.BasisData(jalur_basis)
  dilayani = 0
  ditolak = 0
  lama_layan = []
  gerbang.wait()
  while True:
    request = messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
    if request is None:
      continue
    if request.nomor == NOMOR_BERHENTI:
      break
    jawaban = basis.layani(request, nama)
    lama_layan.append((time.monotonic() - request.waktu_kirim) * MILIDETIK)
    if jawaban.diterima:
      dilayani += 1
    else:
      ditolak += 1
  basis.tutup()
  pencatat.catat(nama, dilayani, ditolak, lama_layan, time.monotonic())


def rakit_versi_space(jumlah_unit: int, jeda_replikasi: float,
                      jalur_basis: str = basis_data.NAMA_BERKAS,
                      per_kelas: int = None,
                      ukuran_penyangga: int = UKURAN_PENYANGGA_BAKU) -> tuple:
  """Merangkai messaging grid, saluran replikasi, pump, writer, dan unitnya.

  Perakitan dikumpulkan di satu fungsi agar skrip pengukuran tidak mengulang
  susunan yang sama. Mengembalikan tuple berisi messaging grid, daftar unit,
  data pump, data writer, dan saluran replikasinya.
  """
  messaging_grid = modul_middleware.MessagingGrid()
  saluran = modul_grid.SaluranReplikasi(jeda_replikasi, jumlah_unit)
  pump = modul_pompa.DataPump()
  writer = modul_pompa.DataWriter(pump, jalur_basis)
  daftar_unit = []
  for nomor in range(1, jumlah_unit + 1):
    daftar_unit.append(ProcessingUnit(f"unit-{nomor}", messaging_grid,
                                      saluran, pump, per_kelas,
                                      ukuran_penyangga, nomor))
  return messaging_grid, daftar_unit, pump, writer, saluran


def jejak_satu_request() -> None:
  """Mencetak jalannya satu request langkah demi langkah beserta angkanya.

  Dipakai naskah bab sebagai jejak nyata, sehingga langkah yang ditulis di sana
  benar-benar berasal dari eksekusi, bukan dari karangan. Tidak mengembalikan
  apa pun.
  """
  basis_data.siapkan_berkas_baru()
  messaging_grid, daftar_unit, pump, writer, saluran = rakit_versi_space(
    jumlah_unit=2, jeda_replikasi=modul_grid.JEDA_REPLIKASI_BAKU)
  unit_satu, unit_dua = daftar_unit
  writer.mulai()

  request = domain.bangkitkan_request(1)[0]
  kode = request.kode_kelas
  print(f"1. Mahasiswa {request.nim} menekan simpan untuk kelas {kode}, "
        f"dan itu menjadi request nomor {request.nomor}.")
  messaging_grid.kirim(request)
  print(f"2. Messaging grid menerima request, antreannya menjadi "
        f"{messaging_grid.panjang()}.")
  diterima = messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
  print(f"3. {unit_satu.nama} yang menganggur mengambilnya dari antrean.")
  print(f"4. Sisa kuota {kode} menurut grid {unit_satu.nama} "
        f"adalah {unit_satu.grid.baca(kode)}.")

  mulai = time.monotonic()
  jawaban = unit_satu.layani(diterima)
  lama = (time.monotonic() - mulai) * MILIDETIK
  print(f"5. Aturan bisnis dijalankan, sisanya menjadi {jawaban.sisa}, "
        f"dan mahasiswa dijawab '{jawaban.alasan}' dalam {lama:.4f} ms.")
  basis_sebelum = basis_data.BasisData()
  print(f"6. Saat itu juga basis data masih mencatat "
        f"{basis_sebelum.baca_sisa(kode)}, sebab data writer belum menulis.")
  basis_sebelum.tutup()
  print(f"7. Sisa menurut grid {unit_dua.nama} juga masih "
        f"{unit_dua.grid.baca(kode)}, sebab replication lag "
        f"{modul_grid.JEDA_REPLIKASI_BAKU * MILIDETIK:.0f} ms belum lewat.")

  time.sleep(modul_grid.JEDA_REPLIKASI_BAKU + 0.02)
  unit_dua.grid.serap_replikasi()
  print(f"8. Sesudah lag lewat, grid {unit_dua.nama} ikut menjadi "
        f"{unit_dua.grid.baca(kode)}.")

  writer.hentikan()
  basis_sesudah = basis_data.BasisData()
  print(f"9. Data pump menyerahkan {pump.jumlah_terkirim()} kiriman, data writer "
        f"menuliskannya dengan {writer.jumlah_commit} commit, dan basis data "
        f"menjadi {basis_sesudah.baca_sisa(kode)}.")
  print("10. Hasil akhirnya, mahasiswa sudah dijawab pada langkah kelima, "
        "sedangkan barisnya tersimpan pada langkah kesembilan.")
  basis_sesudah.tutup()
  for unit in daftar_unit:
    unit.hentikan()
  saluran.tutup()


if __name__ == "__main__":
  jejak_satu_request()
