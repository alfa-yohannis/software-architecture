"""Dua versi processing unit untuk domain yang sama, beserta penulis datanya.

Domainnya satu, yaitu mengonversi berkas setoran valuta asing lalu menyimpan
totalnya. Yang berbeda hanya tempat unit membaca kurs dan tempat unit menaruh
hasil.

UnitBasisData membaca kurs dari SQLite lalu menyimpan hasilnya ke SQLite pada
setiap tugas, sehingga berkas basis data berada di jalur setiap tugas.
UnitRuang membaca kurs dari grid memorinya sendiri lalu menumpuk hasil di
penyangga lokal, dan penyangga itu dikirim ke ruang bersama sekelompok
sekaligus. PenulisData yang kemudian memindahkannya ke SQLite, di luar jalur
tugas.

Cara menjalankan, dengan jumlah unit sebagai argumen:
  python unit.py basis 4
  python unit.py ruang 4
"""

import multiprocessing
import queue
import sqlite3
import sys
import time

import basis_data
import domain
import layanan_ruang

# Banyaknya hasil yang ditahan unit sebelum dikirim ke ruang sekelompok
# sekaligus. Semakin besar angkanya semakin sedikit bolak-balik lewat soket,
# tetapi semakin banyak pula hasil yang lenyap bila unitnya mati.
UKURAN_KELOMPOK = 50
# Batas lama menahan penyangga walaupun belum penuh, dalam detik. Tanpa batas
# ini, unit terakhir yang kebagian sedikit tugas dapat menahan hasilnya sampai
# aplikasi selesai.
JEDA_KIRIM = 0.25
# Lama unit menunggu tugas baru sebelum menyimpulkan ruang sudah kosong.
BATAS_TUNGGU_TUGAS = 0.1
# Lama penulis data menunggu kelompok baru sebelum memeriksa tanda berhenti.
BATAS_TUNGGU_KELOMPOK = 0.05
# Selang memantau kemajuan beban saat menunggu saat yang tepat untuk mematikan
# satu unit, dalam detik.
JEDA_PANTAU = 0.001
# Jumlah tugas baku pada satu kali beban. Angkanya dipilih agar versi ruang
# dengan delapan unit tetap berjalan lebih dari setengah detik, sehingga biaya
# menyalakan proses tidak mendominasi hasilnya.
JUMLAH_TUGAS = 900
PASANGAN_BAKU = ("USD", "IDR")


class UnitBasisData:
  """Processing unit yang menaruh seluruh lalu lintas datanya di basis data.

  Satu objek dipegang satu proses. Koneksinya dibuka sekali lalu dipakai ulang,
  sehingga biaya membuka berkas tidak ikut terhitung pada setiap tugas.
  Perlakuan itu menguntungkan versi ini, dan karena itu selisih yang terukur
  nanti adalah batas bawahnya.
  """

  def __init__(self, nama_unit: str, basis: basis_data.BasisData) -> None:
    """Mencatat nama unit dan basis data yang dipakainya, tanpa membuka koneksi.

    Koneksi belum dibuka di sini sebab objek ini masih berada di proses induk
    ketika dibuat. Koneksi SQLite tidak boleh menyeberang batas proses.
    """
    self.nama_unit = nama_unit
    self.basis = basis
    self.koneksi: sqlite3.Connection | None = None

  def siapkan(self) -> None:
    """Membuka koneksi milik proses ini sendiri sebelum tugas pertama datang.

    Dipanggil di dalam proses anak, bukan di proses induk. Tidak mengembalikan
    apa pun.
    """
    self.koneksi = self.basis.buka_koneksi()

  def kerjakan(self, tugas: domain.Tugas) -> float:
    """Membaca kurs, menghitung total, lalu menyimpan hasilnya dalam satu commit.

    Ketiga langkah itu berada di jalur tugas, dan commit-lah yang paling mahal
    sebab menuntut data benar-benar sampai ke berkas. Mengembalikan float berisi
    latensi layanan satu tugas dalam milidetik.
    """
    mulai = time.perf_counter()
    kurs = self.basis.baca_kurs(self.koneksi, tugas.kode_asal, tugas.kode_tujuan)
    total = domain.hitung_total(tugas, kurs)
    self.basis.simpan_hasil(self.koneksi, [(tugas.nomor, self.nama_unit, total)])
    return (time.perf_counter() - mulai) * 1000.0

  def tutup(self) -> None:
    """Menutup koneksi sesudah seluruh tugas selesai.

    Tidak mengembalikan apa pun. Dipanggil terpisah agar penutupan tidak ikut
    terhitung sebagai latensi tugas terakhir.
    """
    if self.koneksi is not None:
      self.koneksi.close()
      self.koneksi = None


class UnitRuang:
  """Processing unit yang memegang salinan kurs sendiri dan menunda penyimpanan.

  Kurs disalin sekali ke grid memori, lalu dibaca dari sana pada setiap tugas.
  Hasil ditumpuk di penyangga lokal, dan baru dikirim ke ruang setelah
  penyangganya penuh. Karena itu tidak ada satu pun sentuhan berkas di jalur
  tugas, dan itulah sumber kecepatannya sekaligus sumber risikonya.
  """

  def __init__(self, nama_unit: str, ruang_bersama) -> None:
    """Menyiapkan grid memori yang masih kosong beserta penyangga hasilnya.

    Proksi ruang diterima dari luar, sebab unit tidak perlu tahu di proses mana
    ruangnya berada.
    """
    self.nama_unit = nama_unit
    self.ruang = ruang_bersama
    self.grid: dict[tuple[str, str], float] = {}
    self.versi_grid = 0
    self.penyangga: list[tuple[int, str, float]] = []
    self.waktu_kirim = 0.0

  def muat_grid(self) -> int:
    """Menyalin seluruh kurs dari ruang ke grid memori unit ini.

    Penyalinan hanya terjadi sekali, sehingga ribuan tugas berikutnya tidak
    menyentuh ruang sama sekali untuk membaca kurs. Mengembalikan int berisi
    jumlah pasangan mata uang yang tersalin.
    """
    for _, asal, tujuan, nilai, versi in self.ruang.baca_semua(domain.POLA_KURS):
      self.grid[(asal, tujuan)] = nilai
      self.versi_grid = versi
    self.waktu_kirim = time.monotonic()
    return len(self.grid)

  def kerjakan(self, tugas: domain.Tugas) -> float:
    """Menghitung total tugas memakai kurs lokal, lalu menumpuk hasilnya.

    Penyangga dikirim hanya bila sudah penuh atau sudah terlalu lama ditahan,
    sehingga sebagian besar tugas tidak menyentuh ruang sama sekali.
    Mengembalikan float berisi latensi layanan satu tugas dalam milidetik.
    """
    mulai = time.perf_counter()
    kurs = self.grid.get((tugas.kode_asal, tugas.kode_tujuan))
    total = domain.hitung_total(tugas, kurs)
    self.penyangga.append((tugas.nomor, self.nama_unit, total))
    if self.perlu_kirim():
      self.kirim_kelompok()
    return (time.perf_counter() - mulai) * 1000.0

  def perlu_kirim(self) -> bool:
    """Menentukan apakah penyangga sudah layak dikirim ke ruang.

    Dua syarat diperiksa, yaitu penyangga penuh atau sudah lewat batas waktu.
    Mengembalikan True bila salah satu terpenuhi.
    """
    if len(self.penyangga) >= UKURAN_KELOMPOK:
      return True
    return time.monotonic() - self.waktu_kirim >= JEDA_KIRIM

  def kirim_kelompok(self) -> int:
    """Menulis isi penyangga ke ruang sebagai satu tupel kelompok.

    Sesudah tertulis, hasilnya menjadi tanggung jawab penulis data dan aman dari
    matinya unit ini. Mengembalikan int berisi jumlah hasil yang terkirim.
    """
    if not self.penyangga:
      return 0
    terkirim = len(self.penyangga)
    self.ruang.tulis(("kelompok", self.nama_unit, tuple(self.penyangga)))
    self.penyangga.clear()
    self.waktu_kirim = time.monotonic()
    return terkirim


class PenulisData:
  """Pemindah hasil dari ruang ke basis data, berjalan di luar jalur tugas.

  Peran ini yang pada susunan berbasis ruang disebut data pump beserta data
  writer-nya. Kesibukannya tidak pernah menahan satu unit pun, sebab unit hanya
  menitipkan hasil ke ruang lalu langsung melanjutkan tugas berikutnya.
  """

  def __init__(self, ruang_bersama, basis: basis_data.BasisData) -> None:
    """Mencatat ruang asal dan basis data tujuan, tanpa membuka koneksi.

    Sama seperti unit basis data, koneksinya dibuka di dalam proses anak.
    """
    self.ruang = ruang_bersama
    self.basis = basis

  def jalankan(self, henti) -> int:
    """Menguras kelompok dari ruang sampai tanda berhenti menyala dan ruang habis.

    Tanda berhenti saja tidak cukup, sebab masih mungkin ada kelompok yang baru
    ditulis unit terakhir. Karena itu pengurasan berhenti hanya ketika keduanya
    terpenuhi. Mengembalikan int berisi jumlah baris hasil yang tersimpan.
    """
    koneksi = self.basis.buka_koneksi()
    tersimpan = 0
    while True:
      kelompok = self.ruang.ambil(domain.POLA_KELOMPOK, BATAS_TUNGGU_KELOMPOK)
      if kelompok is None:
        if henti.is_set():
          break
        continue
      tersimpan += self.basis.simpan_hasil(koneksi, list(kelompok[2]))
    koneksi.close()
    return tersimpan


def jalankan_unit_basis_data(nama_unit: str, pencacah, jumlah_tugas: int,
                             nama_berkas: str, antrean_laporan) -> None:
  """Menjalankan satu unit versi basis data sampai tidak ada tugas tersisa.

  Nomor tugas diambil dari pencacah bersama, bukan dari basis data, sebab
  pembagian tugas bukan bagian yang sedang diukur. Tidak mengembalikan apa pun,
  sebab laporannya dikirim lewat antrean.
  """
  unit = UnitBasisData(nama_unit, basis_data.BasisData(nama_berkas))
  waktu_mulai = time.monotonic()
  unit.siapkan()
  daftar_latensi = []
  waktu_selesai = waktu_mulai
  while True:
    nomor = ambil_nomor(pencacah, jumlah_tugas)
    if nomor is None:
      break
    daftar_latensi.append(unit.kerjakan(buat_tugas(nomor)))
    waktu_selesai = time.monotonic()
  unit.tutup()
  antrean_laporan.put((nama_unit, waktu_mulai, waktu_selesai, daftar_latensi))


def jalankan_unit_ruang(nama_unit: str, pencacah, jumlah_tugas: int,
                        alamat: tuple, antrean_laporan) -> None:
  """Menjalankan satu unit versi ruang sampai tidak ada tugas tersisa.

  Grid memori dimuat lebih dahulu, lalu penyangga terakhir dikirim sebelum unit
  melaporkan diri. Tidak mengembalikan apa pun, sebab laporannya dikirim lewat
  antrean.
  """
  _, ruang_bersama = layanan_ruang.sambung_layanan(alamat)
  unit = UnitRuang(nama_unit, ruang_bersama)
  waktu_mulai = time.monotonic()
  unit.muat_grid()
  daftar_latensi = []
  waktu_selesai = waktu_mulai
  while True:
    tugas = ambil_tugas(ruang_bersama, pencacah)
    if tugas is None:
      break
    daftar_latensi.append(unit.kerjakan(tugas))
    waktu_selesai = time.monotonic()
  unit.kirim_kelompok()
  antrean_laporan.put((nama_unit, waktu_mulai, waktu_selesai, daftar_latensi))


def jalankan_penulis_data(alamat: tuple, nama_berkas: str, henti) -> None:
  """Menyalakan penulis data di prosesnya sendiri sampai tanda berhenti menyala.

  Proses terpisah dipakai agar commit penulis benar-benar berjalan bersamaan
  dengan pemrosesan, bukan bergantian dengannya. Tidak mengembalikan apa pun,
  sebab yang tersimpan dihitung ulang dari basis data oleh pemanggilnya.
  """
  _, ruang_bersama = layanan_ruang.sambung_layanan(alamat)
  PenulisData(ruang_bersama, basis_data.BasisData(nama_berkas)).jalankan(henti)


def ambil_nomor(pencacah, jumlah_tugas: int) -> int | None:
  """Mengambil satu nomor tugas berikutnya dari pencacah bersama.

  Pencacah ini mewakili pembagi permintaan di depan aplikasi, dan dipakai versi
  basis data. Penaikannya dijaga kunci bawaan Value, sehingga dua unit tidak
  pernah memperoleh nomor yang sama. Mengembalikan int berisi nomor tugas, atau
  None bila seluruh tugas sudah habis dibagikan.
  """
  with pencacah.get_lock():
    nomor = pencacah.value
    if nomor >= jumlah_tugas:
      return None
    pencacah.value = nomor + 1
  return nomor


def ambil_tugas(ruang_bersama, pencacah) -> domain.Tugas | None:
  """Mengambil satu tugas dari ruang, lalu menaikkan pencacah kemajuan.

  Pembagi tugas di sini ruang itu sendiri, sebab satu tupel hanya dapat diambil
  satu unit. Pencacahnya alat ukur belaka, dipakai agar percobaan mematikan unit
  tahu sudah sejauh mana bebannya berjalan. Mengembalikan objek Tugas, atau None
  bila ruang sudah kehabisan tugas.
  """
  tupel = ruang_bersama.ambil(domain.POLA_TUGAS, BATAS_TUNGGU_TUGAS)
  if tupel is None:
    return None
  with pencacah.get_lock():
    pencacah.value += 1
  return domain.Tugas.dari_tupel(tupel)


def buat_tugas(nomor: int) -> domain.Tugas:
  """Membentuk satu tugas baku berisi transaksi sebanyak yang ditentukan domain.

  Seluruh tugas memakai pasangan mata uang yang sama, sehingga perbedaan waktu
  antar tugas hanya berasal dari tempat datanya, bukan dari isinya.
  Mengembalikan objek Tugas.
  """
  return domain.Tugas(nomor, PASANGAN_BAKU[0], PASANGAN_BAKU[1],
                      domain.TRANSAKSI_PER_TUGAS)


def kumpulkan_laporan(antrean_laporan, daftar_proses: list,
                      jeda_akhir: float = 1.0) -> list:
  """Mengambil laporan unit dari antrean tanpa menunggu unit yang sudah mati.

  Selama masih ada unit yang hidup, penantiannya tidak berbatas, sebab beban
  dengan satu unit memang lama. Begitu seluruh unit berhenti, penantian diberi
  tenggang sesaat lalu ditutup, sehingga unit yang dimatikan tidak ditunggu
  selamanya. Mengembalikan list berisi laporan yang sempat terkumpul.
  """
  daftar = []
  tenggat = None
  while len(daftar) < len(daftar_proses):
    try:
      daftar.append(antrean_laporan.get(timeout=0.1))
      continue
    except queue.Empty:
      pass
    if any(proses.is_alive() for proses in daftar_proses):
      tenggat = None
    elif tenggat is None:
      tenggat = time.monotonic() + jeda_akhir
    elif time.monotonic() > tenggat:
      break
  return daftar


def rangkum(daftar_laporan: list, tersimpan: int, jumlah_tugas: int) -> dict:
  """Menggabungkan laporan seluruh unit menjadi satu ringkasan satu beban.

  Lama pemrosesan dihitung dari unit yang paling awal mulai sampai unit yang
  paling akhir selesai, sehingga waktu menyalakan proses tidak ikut terhitung.
  Mengembalikan dict berisi detik, tugas selesai, tugas tersimpan, dan daftar
  latensi gabungan.
  """
  latensi = []
  waktu_mulai = []
  waktu_selesai = []
  for _, mulai, selesai, daftar_latensi in daftar_laporan:
    waktu_mulai.append(mulai)
    waktu_selesai.append(selesai)
    latensi.extend(daftar_latensi)
  detik = max(waktu_selesai) - min(waktu_mulai) if waktu_mulai else 0.0
  return {
    "detik": detik,
    "tugas_selesai": len(latensi),
    "tugas_tersimpan": tersimpan,
    "tugas_hilang": jumlah_tugas - tersimpan,
    "latensi": latensi,
  }


def matikan_satu_unit(daftar_proses: list, pencacah, jumlah_tugas: int,
                      bagian: float | None) -> str | None:
  """Menunggu sampai sebagian beban terbagikan, lalu mengirim SIGKILL ke unit.

  Penantian diikat pada kemajuan pekerjaan, bukan pada jam dinding, sebab
  menyalakan proses anak memakan waktu yang berbeda di setiap mesin. Dengan cara
  ini unit selalu mati pada titik beban yang sama. SIGKILL dipakai, bukan
  penghentian yang sopan, sebab yang ditiru adalah mesin yang mendadak padam.
  Mengembalikan str berisi nama proses yang dimatikan, atau None bila tidak ada
  yang dimatikan.
  """
  if bagian is None:
    return None
  batas = int(jumlah_tugas * bagian)
  while pencacah.value < batas:
    if not any(proses.is_alive() for proses in daftar_proses):
      return None
    time.sleep(JEDA_PANTAU)
  korban = daftar_proses[0]
  if not korban.is_alive():
    return None
  korban.kill()
  return korban.name


def jalankan_versi_basis_data(jumlah_unit: int, jumlah_tugas: int = JUMLAH_TUGAS,
                              nama_berkas: str = basis_data.NAMA_BERKAS,
                              bagian_mematikan: float | None = None) -> dict:
  """Menjalankan satu beban penuh memakai unit versi basis data.

  Basis data disiapkan ulang lebih dahulu, sehingga jumlah baris hasil pada
  akhir beban benar-benar berasal dari beban ini saja. Mengembalikan dict hasil
  rangkum ditambah nama unit yang dimatikan.
  """
  basis = basis_data.BasisData(nama_berkas)
  basis.siapkan()
  pencacah = multiprocessing.Value("i", 0)
  antrean_laporan = multiprocessing.Queue()
  daftar_proses = [
    multiprocessing.Process(
      target=jalankan_unit_basis_data,
      name=f"unit{nomor}",
      args=(f"unit{nomor}", pencacah, jumlah_tugas, nama_berkas,
            antrean_laporan))
    for nomor in range(jumlah_unit)]
  for proses in daftar_proses:
    proses.start()
  dimatikan = matikan_satu_unit(daftar_proses, pencacah, jumlah_tugas,
                                bagian_mematikan)
  daftar_laporan = kumpulkan_laporan(antrean_laporan, daftar_proses)
  for proses in daftar_proses:
    proses.join()
  ringkasan = rangkum(daftar_laporan, len(basis.nomor_tersimpan()), jumlah_tugas)
  ringkasan["dimatikan"] = dimatikan
  return ringkasan


def jalankan_versi_ruang(jumlah_unit: int, jumlah_tugas: int = JUMLAH_TUGAS,
                         nama_berkas: str = basis_data.NAMA_BERKAS,
                         bagian_mematikan: float | None = None) -> dict:
  """Menjalankan satu beban penuh memakai unit versi ruang beserta penulisnya.

  Seluruh tugas ditulis ke ruang lebih dahulu, lalu unit berebut mengambilnya.
  Cara itu lebih mahal daripada pencacah bersama yang dipakai versi basis data,
  sehingga perbandingan hasilnya berpihak kepada versi basis data. Penulis data
  baru diberi tanda berhenti sesudah seluruh unit selesai, agar kelompok
  terakhir tetap sempat tersimpan. Mengembalikan dict hasil rangkum ditambah
  nama unit yang dimatikan.
  """
  basis = basis_data.BasisData(nama_berkas)
  basis.siapkan()
  layanan, ruang_bersama, alamat = layanan_ruang.mulai_layanan()
  for nomor in range(jumlah_tugas):
    ruang_bersama.tulis(buat_tugas(nomor).ke_tupel())
  pencacah = multiprocessing.Value("i", 0)
  antrean_laporan = multiprocessing.Queue()
  henti = multiprocessing.Event()
  penulis = multiprocessing.Process(
    target=jalankan_penulis_data, name="penulis",
    args=(alamat, nama_berkas, henti))
  penulis.start()
  daftar_proses = [
    multiprocessing.Process(
      target=jalankan_unit_ruang,
      name=f"unit{nomor}",
      args=(f"unit{nomor}", pencacah, jumlah_tugas, alamat, antrean_laporan))
    for nomor in range(jumlah_unit)]
  for proses in daftar_proses:
    proses.start()
  dimatikan = matikan_satu_unit(daftar_proses, pencacah, jumlah_tugas,
                                bagian_mematikan)
  daftar_laporan = kumpulkan_laporan(antrean_laporan, daftar_proses)
  for proses in daftar_proses:
    proses.join()
  henti.set()
  penulis.join()
  layanan.shutdown()
  ringkasan = rangkum(daftar_laporan, len(basis.nomor_tersimpan()), jumlah_tugas)
  ringkasan["dimatikan"] = dimatikan
  return ringkasan


if __name__ == "__main__":
  versi = sys.argv[1] if len(sys.argv) > 1 else "ruang"
  unit_diminta = int(sys.argv[2]) if len(sys.argv) > 2 else 4
  pilihan = {"basis": jalankan_versi_basis_data, "ruang": jalankan_versi_ruang}
  hasil = pilihan[versi](unit_diminta)
  print(f"Versi              : {versi}")
  # Keluarannya: Versi              : ruang
  print(f"Processing unit    : {unit_diminta}")
  # Keluarannya: Processing unit    : 4
  print(f"Tugas per detik    : {hasil['tugas_selesai'] / hasil['detik']:.1f}")
  # Keluarannya: Tugas per detik    : 3815.9
  print(f"Tugas tersimpan    : {hasil['tugas_tersimpan']}")
  # Keluarannya: Tugas tersimpan    : 900
