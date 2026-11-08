"""Aturan pengisian rencana studi yang dipakai kedua versi apa adanya.

File ini tidak mengenal basis data, grid, maupun proses. Isinya hanya daftar
kelas mata kuliah beserta kuotanya, bentuk request, dan satu aturan bisnis,
yaitu kuota tidak boleh menjadi minus. Karena itu aturan yang sama dapat
dipakai versi basis data, versi space, dan seluruh skrip pengukuran.

Domainnya dipilih karena bebannya datang serentak. Pengisian rencana studi
dibuka pada jam yang sama bagi seluruh angkatan, sehingga ribuan request
menumpuk pada menit pertama, lalu sepi lagi sesudahnya. Beban seperti itulah
yang dijawab space-based architecture.

Cara menjalankan: python domain.py
"""

import dataclasses
import random

# Kuota awal setiap kelas mata kuliah, yaitu jumlah mahasiswa yang boleh
# diterima. Angkanya kecil agar perebutan kuota terlihat pada percobaan yang
# singkat.
KUOTA_AWAL = {
  "IF231303-A": 40,
  "IF231303-B": 40,
  "IF231401-A": 35,
  "IF231401-B": 35,
  "IF232102-A": 30,
  "IF232102-B": 30,
}

# Nomor versi pertama setiap baris kelas. Angka ini naik setiap kali kuotanya
# berubah, sehingga penerima replikasi dapat mengetahui bahwa salinan yang
# dipegangnya sudah tertinggal.
VERSI_AWAL = 1

# Benih tetap agar deretan request yang dibangkitkan sama pada setiap
# penjalanan, sehingga hasil pengukuran dapat dibandingkan antar putaran.
BENIH_BAKU = 2026

# Awalan nomor induk mahasiswa yang dibangkitkan.
AWALAN_NIM = "20260"

# Dua jenis request. Membaca sisa kuota jauh lebih sering terjadi daripada
# mengambilnya, sebab mahasiswa membuka halaman kelas berkali-kali sebelum
# memutuskan. Pembedaan ini penting, sebab hanya pengambilan yang mengubah
# grid lalu harus dikabarkan ke unit lain.
JENIS_BACA = "baca"
JENIS_AMBIL = "ambil"

# Bagian request yang mengambil kuota pada beban campuran. Sisanya membaca.
BAGIAN_AMBIL_BAKU = 0.10


class KuotaHabis(Exception):
  """Ditolak sebab kuota kelas yang diminta sudah habis.

  Dipakai kedua versi, sehingga penolakan yang sama terjadi pada keduanya dan
  selisih hasil pengukuran tidak berasal dari aturan bisnis yang berbeda.
  """


@dataclasses.dataclass(frozen=True)
class Request:
  """Satu mahasiswa membaca atau mengambil kuota pada satu kelas.

  Bentuknya sengaja kecil, yaitu nomor urut, nomor induk, kode kelas, dan
  jenisnya. Request inilah yang dibagikan messaging grid kepada processing
  unit yang sedang menganggur.
  """

  nomor: int
  nim: str
  kode_kelas: str
  # JENIS_BACA hanya melihat sisa kuota, sedangkan JENIS_AMBIL menguranginya.
  jenis: str = JENIS_AMBIL
  # Waktu request masuk ke messaging grid, dipakai menghitung latensi dari
  # saat mahasiswa menekan simpan sampai jawabannya keluar.
  waktu_kirim: float = 0.0


@dataclasses.dataclass(frozen=True)
class Jawaban:
  """Hasil satu request beserta sisa kuota yang terlihat saat itu.

  Kolom sisa diisi angka yang dilihat unit pada grid memorinya sendiri, bukan
  angka pada basis data. Perbedaan keduanya itulah yang diukur sebagai
  stale read.
  """

  nomor: int
  diterima: bool
  sisa: int
  alasan: str


def kurangi_kuota(sisa: int, request: Request) -> int:
  """Mengurangi satu kuota bila masih ada, lalu mengembalikan sisa barunya.

  Melempar KuotaHabis bila kuotanya sudah nol, sebab kuota yang minus berarti
  kelas menerima mahasiswa melebihi daya tampungnya. Mengembalikan int berisi
  sisa kuota sesudah pengurangan.
  """
  if sisa <= 0:
    raise KuotaHabis(f"kuota {request.kode_kelas} sudah habis")
  return sisa - 1


def bangkitkan_request(jumlah: int, benih: int = BENIH_BAKU,
                       bagian_ambil: float = 1.0) -> list[Request]:
  """Menyusun deretan request yang sama pada setiap penjalanan.

  Kelas dipilih acak dari KUOTA_AWAL, sehingga beberapa request mengenai kelas
  yang sama dan kebersamaan itulah yang menimbulkan tabrakan. Argumen
  bagian_ambil menentukan bagian request yang mengambil kuota, sedangkan
  sisanya hanya membaca. Nilai satu berarti seluruhnya mengambil, yaitu beban
  terberat bagi grid yang direplikasi. Mengembalikan list berisi Request
  sebanyak jumlah yang diminta.
  """
  pengacak = random.Random(benih)
  daftar_kelas = sorted(KUOTA_AWAL)
  daftar_request = []
  for nomor in range(1, jumlah + 1):
    kode_kelas = pengacak.choice(daftar_kelas)
    nim = f"{AWALAN_NIM}{nomor:04d}"
    if pengacak.random() < bagian_ambil:
      jenis = JENIS_AMBIL
    else:
      jenis = JENIS_BACA
    request = Request(nomor, nim, kode_kelas, jenis)
    daftar_request.append(request)
  return daftar_request


def hitung_ambil(daftar_request: list) -> int:
  """Menghitung berapa request pada daftar itu yang mengambil kuota.

  Dipakai skrip pengukuran untuk melaporkan campuran bebannya apa adanya,
  bukan bagian yang diminta. Mengembalikan int berisi jumlah request
  pengambilan.
  """
  jumlah = 0
  for request in daftar_request:
    if request.jenis == JENIS_AMBIL:
      jumlah += 1
  return jumlah


def kuota_awal(per_kelas: int = None) -> dict:
  """Menyalin kuota awal agar pemanggil tidak mengubah tabel acuannya.

  Argumen per_kelas dipakai skrip pengukuran hasil, yaitu ketika kuotanya
  sengaja dibuat banyak agar seluruh request benar-benar dikerjakan, bukan
  ditolak sejak awal. Mengembalikan dict berisi pasangan kode kelas dan sisa
  kuotanya.
  """
  if per_kelas is None:
    return dict(KUOTA_AWAL)
  return {kode: per_kelas for kode in KUOTA_AWAL}


def total_kuota() -> int:
  """Menghitung seluruh kuota yang tersedia pada seluruh kelas.

  Angka ini menjadi batas atas jumlah request yang boleh diterima. Request yang
  melebihinya wajib ditolak. Mengembalikan int berisi jumlah kuota.
  """
  daftar_kuota = KUOTA_AWAL.values()
  return sum(daftar_kuota)


if __name__ == "__main__":
  daftar = bangkitkan_request(10)
  print(f"Kelas mata kuliah : {len(KUOTA_AWAL)}")
  print(f"Kuota seluruhnya  : {total_kuota()}")
  for request in daftar[:5]:
    print(f"  request {request.nomor:3d}  {request.nim}  {request.kode_kelas}")
  sisa_contoh = KUOTA_AWAL[daftar[0].kode_kelas]
  print(f"Sisa sebelum     : {sisa_contoh}")
  sisa_sesudah = kurangi_kuota(sisa_contoh, daftar[0])
  print(f"Sisa sesudah     : {sisa_sesudah}")
  # Keluarannya baris terakhir: Sisa sesudah     : 39
