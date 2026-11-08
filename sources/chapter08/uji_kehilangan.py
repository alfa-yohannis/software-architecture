"""Menguji data loss, yaitu jawaban yang sudah terlanjur diberikan lalu lenyap.

Request dikirim dengan laju tetap, seperti mahasiswa yang berdatangan sepanjang
jam pengisian, lalu satu processing unit dimatikan di tengah jalan. Pada versi
basis data, setiap request sudah tertulis sebelum dijawab, sehingga tidak ada
jawaban yang lenyap. Pada versi space, perubahan yang masih tertahan di
penyangga unit ikut mati bersamanya, padahal mahasiswa sudah menerima jawaban.

Versi space dicoba dengan dua ukuran penyangga. Penyangga satu menyerahkan
setiap perubahan seketika, sedangkan penyangga lima puluh menahannya sampai
penuh lalu menyerahkannya sebagai satu kiriman. Yang dibeli penyangga besar
adalah kiriman ke data pump yang jauh lebih sedikit, sehingga waktu prosesor
untuk mengemas dan memindahkan kiriman ikut turun. Yang dibayarnya adalah
perubahan yang lenyap.

Unit dijalankan sebagai thread di satu proses, sebab yang diukur adalah isi
penyangga ketika unit mati, bukan kecepatan. Mematikan unit berarti
menghentikan thread-nya lalu membuang isi penyangganya tanpa diserahkan,
persis seperti isi memori yang lenyap ketika mesinnya padam.

Yang dilaporkan selisih antara jumlah request yang dijawab dan jumlah baris
yang benar-benar tersimpan. Selisih itulah harga yang dibayar karena
storage dikeluarkan dari jalur request.

Cara menjalankan: python uji_kehilangan.py
"""

import statistics
import time

import basis_data
import domain
import middleware as modul_middleware
import sebaran
import unit as modul_unit

# Banyaknya request pada setiap putaran.
JUMLAH_REQUEST = 3000
# Laju kedatangan request, dalam request per detik.
LAJU_KEDATANGAN = 1000
# Jumlah processing unit yang melayani.
JUMLAH_UNIT = 4
# Banyaknya putaran, sebab satu kali percobaan tidak cukup untuk menyimpulkan.
PUTARAN = 10
# Bagian beban yang sudah terkirim ketika satu unit dimatikan.
BAGIAN_MATI = 0.5
# Kuota tiap kelas, dibuat besar agar seluruh request dikerjakan.
KUOTA_UKUR = 2000
# Replication lag yang dipakai.
JEDA_REPLIKASI = 0.100
# Ukuran penyangga unit yang dicoba pada versi space, yaitu banyaknya
# perubahan yang ditahan di memori sebelum diserahkan kepada data pump.
UKURAN_PENYANGGA_DICOBA = (1, 50)
# Lama menunggu sesudah request terakhir dikirim, agar seluruh unit sempat
# menghabiskan antreannya sebelum dihentikan.
JEDA_SESUDAH_BEBAN = 0.3
# Lebar kolom label dan kolom angka pada ringkasan.
LEBAR_LABEL = 30
LEBAR_KOLOM = 14
MILIDETIK = 1000.0


def kirim_berjadwal(messaging_grid, daftar_request: list, aksi_mati) -> int:
  """Mengirim request dengan laju tetap lalu mematikan satu unit di tengahnya.

  Laju tetap dipakai agar kedua versi menerima beban yang sama bentuknya, dan
  agar unit yang dimatikan benar-benar sedang bekerja. Mengembalikan int berisi
  jumlah perubahan yang lenyap bersama unit itu.
  """
  jeda = 1.0 / LAJU_KEDATANGAN
  jumlah = len(daftar_request)
  batas_mati = int(jumlah * BAGIAN_MATI)
  hilang = 0
  berikutnya = time.monotonic()
  for nomor, request in enumerate(daftar_request, start=1):
    messaging_grid.kirim(request)
    if nomor == batas_mati:
      hilang = aksi_mati()
    berikutnya += jeda
    sisa_waktu = berikutnya - time.monotonic()
    if sisa_waktu > 0:
      time.sleep(sisa_waktu)
  return hilang


def hitung_tersimpan() -> int:
  """Menghitung baris pengambilan yang benar-benar ada di basis data.

  Mengembalikan int berisi jumlah baris pengambilan.
  """
  basis = basis_data.BasisData()
  jumlah = basis.jumlah_pengambilan()
  basis.tutup()
  return jumlah


def jalankan_versi_space(daftar_request: list, ukuran_penyangga: int) -> dict:
  """Menjalankan versi space lalu mematikan satu unit di tengah beban.

  Mengembalikan dict berisi request yang dijawab, baris yang tersimpan,
  selisih keduanya, isi penyangga saat unit mati, banyaknya kiriman ke data
  pump, dan lama melayani setiap request.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid, daftar_unit, pump, writer, saluran = \
    modul_unit.rakit_versi_space(JUMLAH_UNIT, JEDA_REPLIKASI,
                                 basis_data.NAMA_BERKAS, KUOTA_UKUR,
                                 ukuran_penyangga)
  prosesor_awal = time.process_time()
  writer.mulai()
  for unit in daftar_unit:
    unit.mulai()

  unit_mati = daftar_unit[0]
  tertahan = kirim_berjadwal(messaging_grid, daftar_request, unit_mati.mati)
  time.sleep(JEDA_SESUDAH_BEBAN)
  for unit in daftar_unit[1:]:
    unit.hentikan()
  dijawab = 0
  lama_layan = []
  for unit in daftar_unit:
    dijawab += unit.jumlah_dilayani
    lama_layan.extend(unit.lama_layan)
  writer.hentikan()
  prosesor_akhir = time.process_time()
  saluran.tutup()
  tersimpan = hitung_tersimpan()
  return {
    "dijawab": dijawab,
    "tersimpan": tersimpan,
    "hilang": dijawab - tersimpan,
    "tertahan": tertahan,
    "kiriman": writer.jumlah_kiriman,
    "prosesor": (prosesor_akhir - prosesor_awal) * MILIDETIK,
    "lama_layan": lama_layan,
  }


def jalankan_versi_basis_data(daftar_request: list) -> dict:
  """Menjalankan versi basis data lalu mematikan satu unit di tengah beban.

  Mengembalikan dict berisi request yang dijawab, baris yang tersimpan,
  selisih keduanya, dan lama melayani setiap request.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid = modul_middleware.MessagingGrid()
  daftar_unit = []
  for nomor in range(1, JUMLAH_UNIT + 1):
    unit = modul_unit.UnitBasisData(f"unit-{nomor}", messaging_grid,
                                    basis_data.NAMA_BERKAS)
    daftar_unit.append(unit)
  prosesor_awal = time.process_time()
  for unit in daftar_unit:
    unit.mulai()

  unit_mati = daftar_unit[0]
  kirim_berjadwal(messaging_grid, daftar_request, unit_mati.mati)
  time.sleep(JEDA_SESUDAH_BEBAN)
  for unit in daftar_unit[1:]:
    unit.hentikan()
  dijawab = 0
  lama_layan = []
  for unit in daftar_unit:
    dijawab += unit.jumlah_dilayani
    lama_layan.extend(unit.lama_layan)
  prosesor_akhir = time.process_time()
  tersimpan = hitung_tersimpan()
  return {
    "dijawab": dijawab,
    "tersimpan": tersimpan,
    "hilang": dijawab - tersimpan,
    "tertahan": 0,
    "kiriman": 0,
    "prosesor": (prosesor_akhir - prosesor_awal) * MILIDETIK,
    "lama_layan": lama_layan,
  }


def ringkas_versi(daftar_hasil: list) -> dict:
  """Meringkas seluruh putaran satu versi menjadi angka yang dilaporkan.

  Lama melayani seluruh putaran digabung lebih dahulu, agar sebarannya terbaca
  dari seluruh request. Mengembalikan dict berisi median dan nilai terbesar
  yang hilang, banyaknya putaran yang kehilangan, median kiriman ke data pump,
  dan ringkasan lama melayani.
  """
  daftar_hilang = []
  daftar_kiriman = []
  daftar_prosesor = []
  daftar_dijawab = []
  lama_gabungan = []
  putaran_hilang = 0
  for hasil in daftar_hasil:
    daftar_hilang.append(hasil["hilang"])
    daftar_kiriman.append(hasil["kiriman"])
    daftar_prosesor.append(hasil["prosesor"])
    daftar_dijawab.append(hasil["dijawab"])
    lama_gabungan.extend(hasil["lama_layan"])
    if hasil["hilang"] > 0:
      putaran_hilang += 1
  return {
    "median_hilang": statistics.median(daftar_hilang),
    "terbesar_hilang": max(daftar_hilang),
    "putaran_hilang": putaran_hilang,
    "kiriman": statistics.median(daftar_kiriman),
    "prosesor": statistics.median(daftar_prosesor),
    "dijawab": statistics.median(daftar_dijawab),
    "lama_layan": sebaran.ringkas(lama_gabungan),
  }


def cetak_baris_ringkasan(label: str, daftar_nilai: list) -> None:
  """Mencetak satu baris ringkasan dengan lebar kolom yang tetap.

  Tidak mengembalikan apa pun.
  """
  baris = f"{label:<{LEBAR_LABEL}}"
  for nilai in daftar_nilai:
    baris += f"{nilai:>{LEBAR_KOLOM}}"
  print(baris)


def cetak_ringkasan(ringkasan_basis: dict, ringkasan_space: list) -> None:
  """Mencetak perbandingan versi basis data dengan kedua ukuran penyangga.

  Tidak mengembalikan apa pun.
  """
  daftar_versi = [ringkasan_basis] + ringkasan_space
  judul = ["Basis data"]
  for ukuran in UKURAN_PENYANGGA_DICOBA:
    judul.append(f"Penyangga {ukuran}")
  cetak_baris_ringkasan("", judul)
  dijawab = []
  median_hilang = []
  terbesar_hilang = []
  putaran_hilang = []
  kiriman = []
  prosesor = []
  for ringkasan in daftar_versi:
    dijawab.append(f"{ringkasan['dijawab']:.0f}")
    median_hilang.append(f"{ringkasan['median_hilang']:.1f}")
    terbesar_hilang.append(f"{ringkasan['terbesar_hilang']}")
    putaran_hilang.append(f"{ringkasan['putaran_hilang']} dari {PUTARAN}")
    kiriman.append(f"{ringkasan['kiriman']:.0f}")
    prosesor.append(f"{ringkasan['prosesor']:.1f}")
  kiriman[0] = "-"
  cetak_baris_ringkasan("Median dijawab, request", dijawab)
  cetak_baris_ringkasan("Median hilang, request", median_hilang)
  cetak_baris_ringkasan("Terbesar hilang, request", terbesar_hilang)
  cetak_baris_ringkasan("Putaran yang kehilangan", putaran_hilang)
  cetak_baris_ringkasan("Kiriman ke data pump, median", kiriman)
  cetak_baris_ringkasan("Waktu prosesor, median ms", prosesor)
  for kunci, label in (("median", "Lama layan median, ms"),
                       ("p95", "Lama layan p95, ms"),
                       ("terbesar", "Lama layan terbesar, ms")):
    daftar_lama = []
    for ringkasan in daftar_versi:
      daftar_lama.append(f"{ringkasan['lama_layan'][kunci]:.4f}")
    cetak_baris_ringkasan(label, daftar_lama)


if __name__ == "__main__":
  daftar_request_utama = domain.bangkitkan_request(JUMLAH_REQUEST)
  print(f"Beban tiap putaran : {JUMLAH_REQUEST} request, "
        f"{LAJU_KEDATANGAN} per detik")
  print(f"Processing unit    : {JUMLAH_UNIT}, satu dimatikan pada "
        f"{BAGIAN_MATI * 100:.0f} persen beban")
  print(f"Putaran            : {PUTARAN}\n")

  hasil_basis = []
  hasil_space = {ukuran: [] for ukuran in UKURAN_PENYANGGA_DICOBA}
  judul_kolom = f"{'Putaran':>7}{'Basis data':>12}"
  for ukuran in UKURAN_PENYANGGA_DICOBA:
    judul_kolom += f"{'Penyangga ' + str(ukuran):>14}"
  ukuran_terbesar = UKURAN_PENYANGGA_DICOBA[-1]
  judul_kolom += f"{'Isi penyangga ' + str(ukuran_terbesar):>20}"
  print("Request yang dijawab lalu lenyap:")
  print(judul_kolom)
  for putaran in range(1, PUTARAN + 1):
    hasil = jalankan_versi_basis_data(daftar_request_utama)
    hasil_basis.append(hasil)
    baris = f"{putaran:>7}{hasil['hilang']:>12}"
    tertahan = 0
    for ukuran in UKURAN_PENYANGGA_DICOBA:
      hasil = jalankan_versi_space(daftar_request_utama, ukuran)
      hasil_space[ukuran].append(hasil)
      baris += f"{hasil['hilang']:>14}"
      tertahan = hasil["tertahan"]
    baris += f"{tertahan:>20}"
    print(baris)

  print()
  ringkasan_basis_data = ringkas_versi(hasil_basis)
  ringkasan_penyangga = []
  for ukuran in UKURAN_PENYANGGA_DICOBA:
    ringkasan = ringkas_versi(hasil_space[ukuran])
    ringkasan_penyangga.append(ringkasan)
  cetak_ringkasan(ringkasan_basis_data, ringkasan_penyangga)
  # Keluarannya, baris putaran yang kehilangan:
  # Putaran yang kehilangan            0 dari 10     0 dari 10    10 dari 10
