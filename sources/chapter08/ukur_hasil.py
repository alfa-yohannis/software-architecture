"""Mengukur hasil kedua versi dari request dikirim sampai tersimpan.

Beban tiap putaran tetap, yaitu 1.200 request yang dikirim sekaligus seperti
jam pembukaan pengisian rencana studi. Yang diubah hanya jumlah processing
unit, dan setiap unit dijalankan sebagai proses tersendiri agar memakai inti
prosesor sendiri, bukan berbagi satu Global Interpreter Lock.

Tiga waktu dicatat pada setiap putaran:

  Dijawab   sejak request pertama masuk antrean sampai mahasiswa terakhir
            menerima jawaban.
  Tersimpan sejak saat yang sama sampai baris terakhir tertulis di basis data,
            sehingga pekerjaan yang sengaja ditunda ikut terhitung.
  Latensi   sejak satu request masuk antrean sampai mahasiswanya dijawab,
            dihitung per request, lalu dilaporkan sebarannya.

Tanpa waktu kedua, versi space akan terlihat cepat hanya karena storage-nya
belum dikerjakan. Jam mulai ditekan sesudah seluruh unit siap, sehingga lama
menyalakan proses tidak ikut terhitung.

Dua keadaan tambahan memisahkan biaya replikasi dari biaya lainnya. Keadaan
space replikator memindahkan penyebaran message replikasi ke satu proses
tersendiri. Keadaan space tanpa replikasi menghapus replikasinya sama sekali.
Keadaan terakhir itu bukan pilihan yang dapat dipakai, sebab tiap unit lalu
menjual seluruh kuota sendiri-sendiri. Gunanya hanya menjawab satu pertanyaan,
yaitu berapa yang dibayar untuk menyamakan grid seluruh unit.

Putarannya berselang-seling, yaitu satu putaran seluruh keadaan diselesaikan
sebelum putaran berikutnya dimulai. Kesibukan sesaat di luar percobaan karena
itu menimpa seluruh keadaan, bukan satu keadaan saja. Seluruh proses unit
dibuat sebagai daemon, sehingga bila pengukuran gagal di tengah jalan, proses
itu ikut berhenti dan tidak tertinggal memegang prosesor.

Cara menjalankan: python ukur_hasil.py
"""

import multiprocessing
import statistics
import time

import basis_data
import domain
import grid as modul_grid
import middleware as modul_middleware
import pompa as modul_pompa
import sebaran
import unit as modul_unit

MILIDETIK = 1000.0
# Banyaknya request yang dikirim sekaligus pada setiap putaran.
JUMLAH_REQUEST = 1200
# Jumlah processing unit yang dicoba.
JUMLAH_UNIT = (1, 2, 3, 4, 5, 6, 7)
# Prosesor yang diberikan kepada unit, satu prosesor untuk satu unit, agar
# selisih antar jumlah unit tidak tercampur perebutan inti. Mesin percobaan bab
# ini punya delapan inti fisik dengan dua utas tiap inti, yaitu pasangan {0,8},
# {1,9}, sampai {7,15}. Karena itu ketujuh unit memperoleh inti fisik sendiri.
# Pada mesin berinti lebih sedikit, nomor yang tidak ada dilewati, dan unit itu
# berjalan tanpa dikunci.
INTI_UNIT = (0, 1, 2, 3, 4, 5, 6)
# Prosesor bagi satu proses replikator pada keadaan space replikator, dikunci
# sendirian agar biaya menyebarkan message benar-benar dibayar di luar prosesor
# unit.
INTI_REPLIKATOR = 7
# Banyaknya putaran tiap keadaan, sebab satu kali jalan tidak cukup.
PUTARAN = 10
# Dua campuran beban yang dibandingkan. Yang pertama keadaan terberat, yaitu
# setiap request mengubah kuota. Yang kedua meniru jam pengisian rencana studi,
# yaitu sebagian besar mahasiswa melihat sisa kuota lebih dahulu sebelum
# sebagian kecil menekan simpan.
CAMPURAN = (
  (1.00, "seluruhnya mengambil"),
  (domain.BAGIAN_AMBIL_BAKU, "campuran, 10 persen mengambil"),
)
# Keadaan yang dijalankan pada setiap campuran.
KEADAAN = ("basis data", "space", "space replikator", "space tanpa replikasi")
# Kuota tiap kelas mata kuliah selama pengukuran ini, dipilih agar seluruh
# request diterima, bukan ditolak sejak awal.
KUOTA_UKUR = 1000
# Replication lag yang dipakai, yaitu angka pegangan yang sama dengan bukunya.
JEDA_REPLIKASI = 0.100
# Lama menunggu seluruh unit sampai di gerbang, dalam detik.
BATAS_GERBANG = 30.0
# Nomor induk pada request penanda berhenti, yang tidak pernah dilayani.
NIM_PENANDA = "000000000"


class SaluranSenyap(modul_grid.SaluranReplikasi):
  """Saluran yang menelan setiap perubahan, dipakai hanya untuk pembanding.

  Unit yang memakai saluran ini tidak pernah mengabarkan perubahannya, dan
  tidak pernah menerima perubahan unit lain. Jawaban yang dihasilkannya karena
  itu salah, sebab setiap unit menjual seluruh kuota sendiri. Satu-satunya
  gunanya adalah menunjukkan berapa biaya replikasi bila dihapus.
  """

  def terbitkan(self, nomor_pengirim: int,
                pesan: modul_grid.PesanReplikasi) -> None:
    """Membuang message perubahan tanpa mengirimkannya ke mana pun.

    Tidak mengembalikan apa pun.
    """
    return None


def kirim_beban(messaging_grid, daftar_request: list, jumlah_unit: int) -> None:
  """Mengirim seluruh request sekaligus lalu menutupnya dengan penanda berhenti.

  Satu penanda dikirim untuk setiap unit, sehingga tiap unit mengambil tepat
  satu lalu keluar dari perulangannya. Tidak mengembalikan apa pun.
  """
  for request in daftar_request:
    messaging_grid.kirim(request)
  penanda = domain.Request(modul_unit.NOMOR_BERHENTI, NIM_PENANDA, "")
  for _ in range(jumlah_unit):
    messaging_grid.kirim(penanda)


def kuras_antrean(messaging_grid, jumlah: int, pencatat, gerbang) -> None:
  """Mengambil sejumlah request dari antrean secepat mungkin lalu melapor.

  Dipakai hanya untuk mengukur batas messaging grid, yaitu berapa request yang
  dapat berpindah dari pengirim ke satu unit tanpa pekerjaan apa pun di
  dalamnya. Gerbangnya menahan proses ini sampai pengirimnya siap, sehingga
  lama menyalakan proses tidak ikut terhitung. Tidak mengembalikan apa pun.
  """
  gerbang.wait()
  diambil = 0
  while diambil < jumlah:
    request = messaging_grid.ambil(modul_unit.BATAS_TUNGGU_REQUEST)
    if request is not None:
      diambil += 1
  waktu_selesai = time.monotonic()
  pencatat.catat("penguras", diambil, 0, [], waktu_selesai)


def ukur_batas_antrean(daftar_request: list) -> float:
  """Mengukur lama seluruh beban melewati messaging grid tanpa dikerjakan.

  Unit penguras tidak menjalankan aturan bisnis apa pun, sehingga yang terukur
  murni biaya memindahkan request antarproses. Angka inilah batas bawah versi
  space, berapa pun unit yang ditambahkan. Mengembalikan float berisi lama
  seluruh beban melewati antrean, dalam milidetik.
  """
  messaging_grid = modul_middleware.MessagingGrid()
  pencatat = modul_middleware.Pencatat()
  gerbang = multiprocessing.Barrier(2, timeout=BATAS_GERBANG)
  jumlah = len(daftar_request)
  proses = multiprocessing.Process(
    target=kuras_antrean, args=(messaging_grid, jumlah, pencatat, gerbang),
    daemon=True)
  proses.start()
  gerbang.wait()
  mulai = time.monotonic()
  for request in daftar_request:
    messaging_grid.kirim(request)
  _, _, _, selesai = pencatat.ringkas(1)
  proses.join()
  return (selesai - mulai) * MILIDETIK


def hitung_tersimpan() -> int:
  """Menghitung baris pengambilan yang benar-benar ada di basis data.

  Angka ini dibaca dari file-nya, bukan dari pencacah di memori, sehingga
  kiriman yang hilang di tengah jalan tidak ikut terhitung. Mengembalikan int
  berisi jumlah baris pengambilan.
  """
  basis = basis_data.BasisData()
  jumlah = basis.jumlah_pengambilan()
  basis.tutup()
  return jumlah


def siapkan_saluran(jumlah_unit: int, nama_keadaan: str):
  """Membuat saluran replikasi yang sesuai dengan keadaan yang diukur.

  Keadaan space menyebarkan message dari dalam unit, keadaan space replikator
  menitipkannya kepada replikator, dan keadaan space tanpa replikasi tidak
  menyebarkan apa pun. Mengembalikan objek SaluranReplikasi atau SaluranSenyap.
  """
  if nama_keadaan == "space tanpa replikasi":
    return SaluranSenyap(JEDA_REPLIKASI, jumlah_unit)
  if nama_keadaan == "space replikator":
    return modul_grid.SaluranReplikasi(JEDA_REPLIKASI, jumlah_unit,
                                       lewat_hub=True)
  return modul_grid.SaluranReplikasi(JEDA_REPLIKASI, jumlah_unit)


def jalankan_putaran_space(jumlah_unit: int, daftar_request: list,
                           nama_keadaan: str) -> dict:
  """Menjalankan satu putaran versi space lalu mengukurnya dari ujung ke ujung.

  Mahasiswa dijawab dari grid memori tiap unit, sedangkan penulisannya
  dikerjakan data writer sesudahnya. Mengembalikan dict berisi lama dijawab,
  lama tersimpan, daftar latensi seluruh request, dan jumlah baris tersimpan.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid = modul_middleware.MessagingGrid()
  saluran = siapkan_saluran(jumlah_unit, nama_keadaan)
  pump = modul_pompa.DataPump()
  pencatat = modul_middleware.Pencatat()
  pakai_replikator = nama_keadaan == "space replikator"
  jumlah_penunggu = jumlah_unit + 1
  if pakai_replikator:
    jumlah_penunggu += 1
  gerbang = multiprocessing.Barrier(jumlah_penunggu, timeout=BATAS_GERBANG)
  writer = modul_pompa.DataWriter(pump, basis_data.NAMA_BERKAS)
  writer.mulai()

  replikator = None
  if pakai_replikator:
    replikator = multiprocessing.Process(
      target=modul_middleware.jalankan_replikator_proses,
      args=(saluran, INTI_REPLIKATOR, gerbang), daemon=True)
    replikator.start()

  daftar_proses = []
  for nomor in range(1, jumlah_unit + 1):
    proses = multiprocessing.Process(
      target=modul_unit.jalankan_unit_space_proses,
      args=(f"unit-{nomor}", nomor, messaging_grid, saluran, pump, pencatat,
            gerbang, KUOTA_UKUR, modul_unit.UKURAN_PENYANGGA_BAKU,
            INTI_UNIT[nomor - 1]), daemon=True)
    proses.start()
    daftar_proses.append(proses)

  gerbang.wait()
  mulai = time.monotonic()
  kirim_beban(messaging_grid, daftar_request, jumlah_unit)
  dilayani, _, daftar_latensi, selesai = pencatat.ringkas(jumlah_unit)
  for proses in daftar_proses:
    proses.join()
  if replikator is not None:
    saluran.hub.put((0, None))
    replikator.join()
  writer.hentikan()
  tersimpan_pada = time.monotonic()
  saluran.tutup()
  tersimpan = hitung_tersimpan()
  return {
    "lama_jawab": (selesai - mulai) * MILIDETIK,
    "lama_simpan": (tersimpan_pada - mulai) * MILIDETIK,
    "latensi": daftar_latensi,
    "dilayani": dilayani,
    "tersimpan": tersimpan,
  }


def jalankan_putaran_basis_data(jumlah_unit: int,
                                daftar_request: list) -> dict:
  """Menjalankan satu putaran versi basis data lalu mengukurnya.

  Kedua lamanya sama, sebab setiap request sudah tertulis sebelum dijawab.
  Mengembalikan dict berbentuk sama dengan jalankan_putaran_space.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid = modul_middleware.MessagingGrid()
  pencatat = modul_middleware.Pencatat()
  gerbang = multiprocessing.Barrier(jumlah_unit + 1, timeout=BATAS_GERBANG)

  daftar_proses = []
  for nomor in range(1, jumlah_unit + 1):
    proses = multiprocessing.Process(
      target=modul_unit.jalankan_unit_basis_data_proses,
      args=(f"unit-{nomor}", messaging_grid, pencatat, gerbang,
            basis_data.NAMA_BERKAS, INTI_UNIT[nomor - 1]), daemon=True)
    proses.start()
    daftar_proses.append(proses)

  gerbang.wait()
  mulai = time.monotonic()
  kirim_beban(messaging_grid, daftar_request, jumlah_unit)
  dilayani, _, daftar_latensi, selesai = pencatat.ringkas(jumlah_unit)
  for proses in daftar_proses:
    proses.join()
  lama_jawab = (selesai - mulai) * MILIDETIK
  tersimpan = hitung_tersimpan()
  return {
    "lama_jawab": lama_jawab,
    "lama_simpan": lama_jawab,
    "latensi": daftar_latensi,
    "dilayani": dilayani,
    "tersimpan": tersimpan,
  }


def jalankan_satu_putaran(nama_keadaan: str, jumlah_unit: int,
                          daftar_request: list) -> dict:
  """Memilih penjalan putaran yang sesuai dengan nama keadaannya.

  Mengembalikan dict hasil satu putaran, berbentuk sama bagi seluruh keadaan.
  """
  if nama_keadaan == "basis data":
    return jalankan_putaran_basis_data(jumlah_unit, daftar_request)
  return jalankan_putaran_space(jumlah_unit, daftar_request, nama_keadaan)


def ringkas_keadaan(nama_keadaan: str, jumlah_unit: int,
                    daftar_hasil: list) -> dict:
  """Meringkas seluruh putaran satu keadaan menjadi satu baris laporan.

  Lama yang dilaporkan adalah median dari seluruh putaran, sedangkan latensi
  seluruh putaran digabung lebih dahulu agar sebarannya terbaca dari seluruh
  request, bukan dari satu putaran saja. Mengembalikan dict berisi ringkasan
  keadaan itu.
  """
  daftar_lama_jawab = []
  daftar_lama_simpan = []
  daftar_dijawab = []
  daftar_tersimpan = []
  latensi_gabungan = []
  for hasil in daftar_hasil:
    daftar_lama_jawab.append(hasil["lama_jawab"])
    daftar_lama_simpan.append(hasil["lama_simpan"])
    daftar_dijawab.append(hasil["dilayani"])
    daftar_tersimpan.append(hasil["tersimpan"])
    latensi_gabungan.extend(hasil["latensi"])
  hasil_terakhir = daftar_hasil[-1]
  jumlah_baris = hasil_terakhir["tersimpan"]
  lama_jawab = statistics.median(daftar_lama_jawab)
  lama_simpan = statistics.median(daftar_lama_simpan)
  return {
    "nama": nama_keadaan,
    "unit": jumlah_unit,
    "lama_jawab": lama_jawab,
    "lama_simpan": lama_simpan,
    "dijawab_per_detik": JUMLAH_REQUEST / lama_jawab * MILIDETIK,
    "tersimpan_per_detik": jumlah_baris / lama_simpan * MILIDETIK,
    "jawab_tercepat": min(daftar_lama_jawab),
    "jawab_terlama": max(daftar_lama_jawab),
    "sebaran": sebaran.ringkas(latensi_gabungan),
    "tersimpan": jumlah_baris,
    "dijawab_terkecil": min(daftar_dijawab),
    "dijawab_terbesar": max(daftar_dijawab),
    "tersimpan_terkecil": min(daftar_tersimpan),
    "tersimpan_terbesar": max(daftar_tersimpan),
  }


def jalankan_satu_campuran(daftar_request: list) -> list:
  """Menjalankan seluruh keadaan pada satu campuran beban, berselang-seling.

  Mengembalikan list berisi list ringkasan, satu list untuk setiap jumlah unit,
  dan di dalamnya satu ringkasan untuk setiap keadaan menurut urutan KEADAAN.
  """
  kumpulan_hasil = {}
  for jumlah in JUMLAH_UNIT:
    for nama_keadaan in KEADAAN:
      kumpulan_hasil[(jumlah, nama_keadaan)] = []
  for _ in range(PUTARAN):
    for jumlah in JUMLAH_UNIT:
      for nama_keadaan in KEADAAN:
        hasil = jalankan_satu_putaran(nama_keadaan, jumlah, daftar_request)
        kumpulan_hasil[(jumlah, nama_keadaan)].append(hasil)
  kumpulan = []
  for jumlah in JUMLAH_UNIT:
    baris_keadaan = []
    for nama_keadaan in KEADAAN:
      daftar_hasil = kumpulan_hasil[(jumlah, nama_keadaan)]
      ringkasan = ringkas_keadaan(nama_keadaan, jumlah, daftar_hasil)
      baris_keadaan.append(ringkasan)
    kumpulan.append(baris_keadaan)
  return kumpulan


def cetak_tabel_laju(kumpulan: list) -> None:
  """Mencetak laju dijawab, laju tersimpan, dan lama dijawab tiap keadaan.

  Labelnya memakai istilah yang sama dengan naskah bab, sebab langkah latihan
  menyuruh mahasiswa mencatat baris ini. Tidak mengembalikan apa pun.
  """
  print(f"{'Unit':>4} {'Keadaan':<21} {'Dijawab/detik':>14} "
        f"{'Tersimpan/detik':>16} {'Lama jawab ms':>14}")
  for baris_keadaan in kumpulan:
    for hasil in baris_keadaan:
      print(f"{hasil['unit']:>4} {hasil['nama']:<21} "
            f"{hasil['dijawab_per_detik']:14.1f} "
            f"{hasil['tersimpan_per_detik']:16.1f} "
            f"{hasil['lama_jawab']:14.1f}")


def cetak_tabel_latensi(kumpulan: list) -> None:
  """Mencetak sebaran latensi per request, gabungan seluruh putaran.

  Median, persentil ke-95, dan nilai terbesar dicetak berdampingan, sebab
  antrean hanya terlihat pada nilai terbesar. Tidak mengembalikan apa pun.
  """
  print(f"{'Unit':>4} {'Keadaan':<21} {'Median':>10} {'p95':>10} "
        f"{'Terbesar':>10}")
  for baris_keadaan in kumpulan:
    for hasil in baris_keadaan:
      ringkasan = hasil["sebaran"]
      print(f"{hasil['unit']:>4} {hasil['nama']:<21} "
            f"{ringkasan['median']:10.2f} {ringkasan['p95']:10.2f} "
            f"{ringkasan['terbesar']:10.2f}")


def cetak_tabel_ragam(kumpulan: list) -> None:
  """Mencetak sebaran lama dijawab antar putaran bagi setiap keadaan.

  Selisih antar keadaan baru layak disebut ada bila lebih besar daripada jarak
  tercepat ke terlama di baris ini. Tidak mengembalikan apa pun.
  """
  print(f"{'Unit':>4} {'Keadaan':<21} {'Tercepat':>10} {'Median':>10} "
        f"{'Terlama':>10}")
  for baris_keadaan in kumpulan:
    for hasil in baris_keadaan:
      print(f"{hasil['unit']:>4} {hasil['nama']:<21} "
            f"{hasil['jawab_tercepat']:10.1f} {hasil['lama_jawab']:10.1f} "
            f"{hasil['jawab_terlama']:10.1f}")


def cetak_tabel_perbandingan(kumpulan: list) -> None:
  """Mencetak perbandingan lama dijawab antar keadaan pada tiap jumlah unit.

  Kolom pertama menunjukkan berapa kali versi space lebih cepat daripada versi
  basis data. Kolom kedua berapa kali replikasi memperlambat versi space, dan
  kolom ketiga berapa kali replikator terpisah mempercepatnya. Tidak
  mengembalikan apa pun.
  """
  print(f"{'Unit':>4} {'Basis data/space':>17} {'Space/tanpa replikasi':>22} "
        f"{'Space/replikator':>17}")
  for baris_keadaan in kumpulan:
    hasil_basis, hasil_space, hasil_hub, hasil_senyap = baris_keadaan
    lebih_cepat = hasil_basis["lama_jawab"] / hasil_space["lama_jawab"]
    biaya_replikasi = hasil_space["lama_jawab"] / hasil_senyap["lama_jawab"]
    bantuan_hub = hasil_space["lama_jawab"] / hasil_hub["lama_jawab"]
    print(f"{hasil_basis['unit']:>4} {lebih_cepat:17.1f} "
          f"{biaya_replikasi:22.1f} {bantuan_hub:17.1f}")


def cetak_tepat_sekali(kumpulan: list) -> None:
  """Mencetak jumlah request yang dijawab dan tersimpan pada seluruh putaran.

  Messaging grid menjanjikan setiap request diambil tepat satu unit. Bila
  janji itu dilanggar, jumlah dijawab pada satu putaran akan melebihi atau
  kurang dari jumlah request yang dikirim. Tidak mengembalikan apa pun.
  """
  dijawab_terkecil = JUMLAH_REQUEST * 2
  dijawab_terbesar = 0
  tersimpan_terkecil = JUMLAH_REQUEST * 2
  tersimpan_terbesar = 0
  jumlah_putaran = 0
  for baris_keadaan in kumpulan:
    for hasil in baris_keadaan:
      dijawab_terkecil = min(dijawab_terkecil, hasil["dijawab_terkecil"])
      dijawab_terbesar = max(dijawab_terbesar, hasil["dijawab_terbesar"])
      tersimpan_terkecil = min(tersimpan_terkecil,
                               hasil["tersimpan_terkecil"])
      tersimpan_terbesar = max(tersimpan_terbesar,
                               hasil["tersimpan_terbesar"])
      jumlah_putaran += PUTARAN
  print(f"Dijawab tiap putaran   : {dijawab_terkecil} sampai "
        f"{dijawab_terbesar} request, pada {jumlah_putaran} putaran")
  print(f"Tersimpan tiap putaran : {tersimpan_terkecil} sampai "
        f"{tersimpan_terbesar} baris")


def cetak_campuran(judul: str, jumlah_ambil: int, kumpulan: list) -> None:
  """Mencetak keempat tabel hasil satu campuran beban.

  Jumlah request yang mengambil kuota dicetak apa adanya, bukan bagian yang
  diminta, sebab pengacaknya tidak menghasilkan bagian yang persis sama.
  Tidak mengembalikan apa pun.
  """
  print(f"\nBeban {judul}: {jumlah_ambil} dari {JUMLAH_REQUEST} request "
        f"mengambil kuota")
  cetak_tabel_laju(kumpulan)
  print("\nLatensi per request dalam ms, gabungan seluruh putaran:")
  cetak_tabel_latensi(kumpulan)
  print("\nRagam lama jawab antar putaran, dalam ms:")
  cetak_tabel_ragam(kumpulan)
  print("\nPerbandingan lama jawab, dalam kali:")
  cetak_tabel_perbandingan(kumpulan)
  print()
  cetak_tepat_sekali(kumpulan)


if __name__ == "__main__":
  multiprocessing.set_start_method("spawn", force=True)
  daftar_teks_inti = [str(inti) for inti in INTI_UNIT]
  daftar_inti = ", ".join(daftar_teks_inti)
  print(f"Beban tiap keadaan : {JUMLAH_REQUEST} request serentak, "
        f"{PUTARAN} putaran berselang-seling")
  print(f"Kuota tiap kelas   : {KUOTA_UKUR} mahasiswa")
  print(f"Replication lag    : {JEDA_REPLIKASI * MILIDETIK:.0f} ms")
  print(f"Prosesor unit      : CPU {daftar_inti}, satu unit satu prosesor")
  print(f"Prosesor replikator: CPU {INTI_REPLIKATOR}, dipakai keadaan "
        f"space replikator")
  daftar_request_batas = domain.bangkitkan_request(JUMLAH_REQUEST)
  batas_antrean = ukur_batas_antrean(daftar_request_batas)
  print(f"Batas messaging grid : {batas_antrean:.1f} ms untuk "
        f"{JUMLAH_REQUEST} request tanpa pekerjaan di unit")

  for bagian, nama_campuran in CAMPURAN:
    daftar_request_campuran = domain.bangkitkan_request(
      JUMLAH_REQUEST, bagian_ambil=bagian)
    jumlah_ambil = domain.hitung_ambil(daftar_request_campuran)
    hasil_campuran = jalankan_satu_campuran(daftar_request_campuran)
    cetak_campuran(nama_campuran, jumlah_ambil, hasil_campuran)
  # Keluarannya, baris tujuh unit space replikator pada beban pertama:
  #    7 space replikator             36404.5          10788.9           33.0
