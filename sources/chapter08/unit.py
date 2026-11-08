"""Processing unit kedua versi, yaitu versi space dan versi basis data.

Versi space melayani request dari grid memorinya sendiri, lalu menitipkan
perubahannya kepada data pump. Versi basis data membuka satu transaksi ke
basis data untuk setiap request. Keduanya memakai aturan bisnis yang sama dari
domain.py, sehingga selisih hasil pengukurannya benar-benar berasal dari cara
menyimpan, bukan dari cara menghitung.

Menjalankan file ini mencetak jejak satu request langkah demi langkah, mulai
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
# Lama menunggu thread unit selesai ketika unit dihentikan atau dimatikan.
BATAS_TUNGGU_THREAD = 2.0
# Nomor request penanda berhenti. Satu penanda dikirim untuk setiap unit,
# sehingga tiap unit mengambil tepat satu lalu keluar dari perulangannya.
NOMOR_BERHENTI = -1
# Banyaknya perubahan yang ditahan di memori unit sebelum diserahkan kepada
# data pump sebagai satu kiriman. Nilai satu berarti setiap perubahan langsung
# diserahkan, sehingga tidak ada yang tertahan. Nilai yang lebih besar membuat
# kirimannya lebih sedikit, tetapi perubahan yang masih tertahan akan lenyap
# bila unitnya mati.
UKURAN_PENYANGGA_BAKU = 1
# Tambahan waktu tunggu pada jejak, agar replication lag benar-benar lewat.
TAMBAHAN_TUNGGU_JEJAK = 0.02


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
    ke penyangga. Request yang hanya membaca berhenti pada langkah kedua,
    sehingga tidak menitipkan apa pun dan tidak mengabarkan apa pun.
    Mengembalikan Jawaban berisi hasil beserta sisa kuota yang terlihat unit
    ini.
    """
    self.grid.serap_replikasi()
    if request.jenis == domain.JENIS_BACA:
      self.jumlah_dilayani += 1
      sisa = self.grid.baca(request.kode_kelas)
      return domain.Jawaban(request.nomor, True, sisa, "sisa dibaca")
    try:
      sisa_baru = self.grid.kurangi(request)
    except domain.KuotaHabis as galat:
      self.jumlah_ditolak += 1
      alasan = str(galat)
      return domain.Jawaban(request.nomor, False, 0, alasan)
    perubahan = modul_pompa.Perubahan(request.nomor, request.nim,
                                      request.kode_kelas, sisa_baru, self.nama)
    self.penyangga.append(perubahan)
    if len(self.penyangga) >= self.ukuran_penyangga:
      self.serahkan_penyangga()
    self.jumlah_dilayani += 1
    return domain.Jawaban(request.nomor, True, sisa_baru, "diterima")

  def serahkan_penyangga(self) -> int:
    """Menyerahkan seluruh isi penyangga kepada data pump sebagai satu kiriman.

    Penyangga diganti dengan daftar baru sebelum dikirim, sebab antrean
    antarproses baru mengemas isinya belakangan, dan daftar yang masih diubah
    akan ikut terkemas dalam keadaan berubah. Mengembalikan int berisi jumlah
    perubahan yang diserahkan.
    """
    kelompok = self.penyangga
    if not kelompok:
      return 0
    self.penyangga = []
    self.pump.kirim(kelompok)
    return len(kelompok)

  def mati(self) -> int:
    """Mematikan unit ini seketika, sehingga isi penyangganya ikut lenyap.

    Dipakai uji_kehilangan.py untuk meniru mesin yang padam di tengah beban.
    Thread-nya dibiarkan menuntaskan request yang sedang dipegang, lalu isi
    penyangganya dibuang tanpa diserahkan. Mengembalikan int berisi jumlah
    perubahan yang lenyap bersama unit ini.
    """
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=BATAS_TUNGGU_THREAD)
    hilang = len(self.penyangga)
    self.penyangga = []
    return hilang

  def jalankan(self) -> None:
    """Mengambil request dari messaging grid sampai tanda berhenti menyala.

    Lama melayani dicatat sejak request diambil sampai jawabannya siap, tanpa
    lama menunggu di antrean, sehingga yang terukur adalah biaya unit itu
    sendiri. Tidak mengembalikan apa pun.
    """
    while not self.berhenti.is_set():
      request = self.messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
      if request is None:
        self.grid.serap_replikasi()
        continue
      mulai = time.monotonic()
      self.layani(request)
      selesai = time.monotonic()
      self.lama_layan.append((selesai - mulai) * MILIDETIK)

  def mulai(self) -> None:
    """Menjalankan unit ini pada thread tersendiri.

    Thread dipakai pada uji_kehilangan.py, sebab yang diukur di sana adalah
    isi penyangga, bukan kecepatan, sehingga unit tidak perlu memakai prosesor
    sendiri. Tidak mengembalikan apa pun.
    """
    self.utas = threading.Thread(target=self.jalankan, daemon=True)
    self.utas.start()

  def hentikan(self) -> None:
    """Menghentikan unit ini dengan tertib, lalu menyerahkan isi penyangganya.

    Thread-nya dihentikan lebih dahulu, sehingga tidak ada perubahan baru yang
    masuk penyangga sesudah penyangga itu diserahkan. Tidak mengembalikan apa
    pun.
    """
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=BATAS_TUNGGU_THREAD)
    self.serahkan_penyangga()


class UnitBasisData:
  """Unit pembanding yang membuka transaksi basis data pada setiap request.

  Aturan bisnisnya sama persis, dan yang berbeda hanya tempat kuotanya dibaca
  serta ditulis. Setiap request karena itu menunggu giliran menulis ke file
  yang sama.
  """

  def __init__(self, nama: str, messaging_grid, jalur_basis: str) -> None:
    """Menyimpan nama unit beserta file basis data yang dipakainya.

    Koneksinya belum dibuka di sini, melainkan di dalam thread unit, sebab
    koneksi SQLite hanya boleh dipakai thread yang membukanya.
    """
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

    Lama melayani diukur dengan cara yang sama dengan ProcessingUnit, sehingga
    keduanya dapat dibandingkan langsung. Tidak mengembalikan apa pun.
    """
    basis = basis_data.BasisData(self.jalur_basis)
    while not self.berhenti.is_set():
      request = self.messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
      if request is None:
        continue
      mulai = time.monotonic()
      jawaban = basis.layani(request, self.nama)
      selesai = time.monotonic()
      self.lama_layan.append((selesai - mulai) * MILIDETIK)
      if jawaban.diterima:
        self.jumlah_dilayani += 1
      else:
        self.jumlah_ditolak += 1
    basis.tutup()

  def mulai(self) -> None:
    """Menjalankan unit ini pada thread tersendiri.

    Bentuknya sama dengan ProcessingUnit.mulai, sehingga uji_kehilangan.py
    memperlakukan kedua versi dengan cara yang sama. Tidak mengembalikan apa
    pun.
    """
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
    """Menghentikan unit ini lalu menunggu threadnya selesai.

    Request yang sedang dipegang tetap dituntaskan, termasuk commit-nya.
    Tidak mengembalikan apa pun.
    """
    self.berhenti.set()
    if self.utas is not None:
      self.utas.join(timeout=BATAS_TUNGGU_THREAD)


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
  Latensinya dihitung sejak request masuk antrean, sehingga lama menunggu
  giliran ikut terhitung. Tidak mengembalikan apa pun.
  """
  modul_middleware.kunci_ke_inti(inti)
  unit = ProcessingUnit(nama, messaging_grid, saluran, pump, per_kelas,
                        ukuran_penyangga, nomor_unit)
  daftar_latensi = []
  gerbang.wait()
  while True:
    request = messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
    if request is None:
      continue
    if request.nomor == NOMOR_BERHENTI:
      break
    unit.layani(request)
    dijawab = time.monotonic()
    daftar_latensi.append((dijawab - request.waktu_kirim) * MILIDETIK)
  unit.serahkan_penyangga()
  waktu_selesai = time.monotonic()
  pencatat.catat(nama, unit.jumlah_dilayani, unit.jumlah_ditolak,
                 daftar_latensi, waktu_selesai)
  saluran.lepas_tanpa_menunggu()


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
  daftar_latensi = []
  gerbang.wait()
  while True:
    request = messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
    if request is None:
      continue
    if request.nomor == NOMOR_BERHENTI:
      break
    jawaban = basis.layani(request, nama)
    dijawab = time.monotonic()
    daftar_latensi.append((dijawab - request.waktu_kirim) * MILIDETIK)
    if jawaban.diterima:
      dilayani += 1
    else:
      ditolak += 1
  basis.tutup()
  waktu_selesai = time.monotonic()
  pencatat.catat(nama, dilayani, ditolak, daftar_latensi, waktu_selesai)


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
    unit = ProcessingUnit(f"unit-{nomor}", messaging_grid, saluran, pump,
                          per_kelas, ukuran_penyangga, nomor)
    daftar_unit.append(unit)
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
  lag_milidetik = modul_grid.JEDA_REPLIKASI_BAKU * MILIDETIK

  daftar_request = domain.bangkitkan_request(1)
  request = daftar_request[0]
  kode = request.kode_kelas
  print(f"1. Mahasiswa {request.nim} menekan simpan untuk kelas {kode}.")
  messaging_grid.kirim(request)
  print(f"2. Messaging grid menerima request nomor {request.nomor}, "
        f"antreannya menjadi {messaging_grid.panjang()}.")
  diterima = messaging_grid.ambil(BATAS_TUNGGU_REQUEST)
  print(f"3. {unit_satu.nama} yang menganggur mengambil request itu "
        f"dari antrean.")
  print(f"4. Sisa kuota {kode} menurut grid {unit_satu.nama} "
        f"adalah {unit_satu.grid.baca(kode)}.")

  mulai = time.monotonic()
  jawaban = unit_satu.layani(diterima)
  selesai = time.monotonic()
  lama = (selesai - mulai) * MILIDETIK
  print(f"5. Sisanya menjadi {jawaban.sisa}, dan mahasiswa dijawab "
        f"'{jawaban.alasan}' dalam {lama:.4f} ms.")
  basis_sebelum = basis_data.BasisData()
  print(f"6. Saat itu basis data masih mencatat "
        f"{basis_sebelum.baca_sisa(kode)}, sebab data writer belum menulis.")
  basis_sebelum.tutup()
  print(f"7. Grid {unit_dua.nama} juga masih {unit_dua.grid.baca(kode)}, "
        f"sebab replication lag {lag_milidetik:.0f} ms belum lewat.")

  time.sleep(modul_grid.JEDA_REPLIKASI_BAKU + TAMBAHAN_TUNGGU_JEJAK)
  unit_dua.grid.serap_replikasi()
  print(f"8. Sesudah lag lewat, grid {unit_dua.nama} ikut menjadi "
        f"{unit_dua.grid.baca(kode)}.")

  writer.hentikan()
  print(f"9. Data pump menerima {writer.jumlah_kiriman} kiriman, lalu data "
        f"writer menulisnya dengan {writer.jumlah_commit} commit.")
  basis_sesudah = basis_data.BasisData()
  print(f"10. Basis data kini mencatat {basis_sesudah.baca_sisa(kode)}, "
        f"sesudah mahasiswanya dijawab di langkah 5.")
  basis_sesudah.tutup()
  for unit in daftar_unit:
    unit.hentikan()
  saluran.tutup()


if __name__ == "__main__":
  jejak_satu_request()
  # Keluarannya baris kelima:
  # 5. Sisanya menjadi 39, dan mahasiswa dijawab 'diterima' dalam 0.3433 ms.
