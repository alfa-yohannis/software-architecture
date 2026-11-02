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

Tanpa waktu kedua, versi space akan terlihat cepat hanya karena penyimpanannya
belum dikerjakan. Jam mulai ditekan sesudah seluruh unit siap, sehingga lama
menyalakan proses tidak ikut terhitung.

Keadaan ketiga, yaitu space tanpa replikasi, dijalankan untuk memisahkan biaya
replikasi dari biaya lainnya. Keadaan itu bukan pilihan yang dapat dipakai,
sebab tiap unit lalu menjual seluruh kuota sendiri-sendiri. Gunanya hanya
menjawab satu pertanyaan, yaitu berapa yang dibayar untuk menyamakan grid
seluruh unit.

Cara menjalankan: python ukur_hasil.py
"""

import multiprocessing
import os
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
# selisih antar jumlah unit tidak tercampur perebutan inti. Mesin percobaan
# punya empat inti fisik dengan dua utas tiap inti, yaitu pasangan {0,4},
# {1,5}, {2,6}, dan {3,7}. Karena itu unit kesatu sampai keempat memperoleh
# inti fisik sendiri, sedangkan unit kelima sampai ketujuh berbagi inti fisik
# dengan unit kesatu sampai ketiga.
INTI_UNIT = (0, 1, 2, 3, 4, 5, 6)
# Prosesor bagi satu proses replikator pada keadaan replikasi terpisah,
# dikunci sendirian agar biaya menyebarkan pesan benar-benar dibayar di luar
# prosesor unit.
INTI_REPLIKATOR = 7
# Banyaknya putaran tiap keadaan, sebab satu kali jalan tidak cukup.
PUTARAN = 5
# Dua campuran beban yang dibandingkan. Yang pertama meniru jam pengisian
# rencana studi, yaitu sebagian besar mahasiswa melihat sisa kuota lebih dahulu
# sebelum sebagian kecil menekan simpan. Yang kedua keadaan terberat, yaitu
# setiap request mengubah kuota.
CAMPURAN = (
  (domain.BAGIAN_AMBIL_BAKU, "campuran, 10 persen mengambil"),
  (1.00, "seluruhnya mengambil"),
)
# Keadaan yang dijalankan pada setiap campuran. Keadaan ketiga memindahkan
# penyebaran pesan replikasi ke satu proses replikator, sedangkan keadaan
# keempat menghapus replikasinya sama sekali sebagai batas bawah.
KEADAAN = ("basis data", "space", "space replikator", "space tanpa replikasi")
# Kuota tiap kelas mata kuliah selama pengukuran ini, dipilih agar seluruh
# request diterima, bukan ditolak sejak awal.
KUOTA_UKUR = 1000
# Replication lag yang dipakai, yaitu angka pegangan yang sama dengan bukunya.
JEDA_REPLIKASI = 0.100
# Lama menunggu seluruh unit sampai di gerbang, dalam detik.
BATAS_GERBANG = 30.0


class SaluranSenyap(modul_grid.SaluranReplikasi):
  """Saluran yang menelan setiap perubahan, dipakai hanya untuk pembanding.

  Unit yang memakai saluran ini tidak pernah mengabarkan perubahannya, dan
  tidak pernah menerima perubahan unit lain. Jawaban yang dihasilkannya karena
  itu salah, sebab setiap unit menjual seluruh kuota sendiri. Satu-satunya
  gunanya adalah menunjukkan berapa biaya replikasi bila dihapus.
  """

  def terbitkan(self, nomor_pengirim: int,
                pesan: modul_grid.PesanReplikasi) -> None:
    """Membuang pesan perubahan tanpa mengirimkannya ke mana pun.

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
  for _ in range(jumlah_unit):
    messaging_grid.kirim(domain.Request(modul_unit.NOMOR_BERHENTI,
                                        "000000000", ""))


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
  pencatat.catat("penguras", diambil, 0, [], time.monotonic())


def ukur_batas_antrean(daftar_request: list) -> float:
  """Mengukur berapa request per detik yang mampu dilewatkan messaging grid.

  Unit penguras tidak menjalankan aturan bisnis apa pun, sehingga yang terukur
  murni biaya memindahkan request antarproses. Angka inilah batas bawah versi
  space, berapa pun unit yang ditambahkan. Mengembalikan float berisi lama
  seluruh beban melewati antrean, dalam milidetik.
  """
  messaging_grid = modul_middleware.MessagingGrid()
  pencatat = modul_middleware.Pencatat()
  gerbang = multiprocessing.Barrier(2, timeout=BATAS_GERBANG)
  proses = multiprocessing.Process(
    target=kuras_antrean,
    args=(messaging_grid, len(daftar_request), pencatat, gerbang))
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

  Angka ini dibaca dari berkasnya, bukan dari pencacah di memori, sehingga
  kiriman yang hilang di tengah jalan tidak ikut terhitung. Mengembalikan int
  berisi jumlah baris pengambilan.
  """
  basis = basis_data.BasisData()
  jumlah = basis.jumlah_pengambilan()
  basis.tutup()
  return jumlah


def siapkan_saluran(jumlah_unit: int, mode: str):
  """Membuat saluran replikasi yang sesuai dengan keadaan yang diukur.

  Mode "replikasi" menyebarkan pesan dari dalam unit, mode "hub" menitipkannya
  kepada replikator, dan mode "senyap" tidak menyebarkan apa pun.
  Mengembalikan objek SaluranReplikasi atau SaluranSenyap.
  """
  if mode == "senyap":
    return SaluranSenyap(JEDA_REPLIKASI, jumlah_unit)
  if mode == "hub":
    return modul_grid.SaluranReplikasi(JEDA_REPLIKASI, jumlah_unit,
                                       lewat_hub=True)
  return modul_grid.SaluranReplikasi(JEDA_REPLIKASI, jumlah_unit)


def jalankan_putaran_space(jumlah_unit: int, daftar_request: list,
                           mode: str) -> dict:
  """Menjalankan satu putaran versi space lalu mengukurnya dari ujung ke ujung.

  Mahasiswa dijawab dari grid memori tiap unit, sedangkan penulisannya
  dikerjakan data writer sesudahnya. Mengembalikan dict berisi kedua laju per
  detik beserta daftar latensi seluruh request putaran ini.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid = modul_middleware.MessagingGrid()
  saluran = siapkan_saluran(jumlah_unit, mode)
  pump = modul_pompa.DataPump()
  pencatat = modul_middleware.Pencatat()
  jumlah_penunggu = jumlah_unit + 1
  if mode == "hub":
    jumlah_penunggu += 1
  gerbang = multiprocessing.Barrier(jumlah_penunggu, timeout=BATAS_GERBANG)
  writer = modul_pompa.DataWriter(pump, basis_data.NAMA_BERKAS)
  writer.mulai()

  replikator = None
  if mode == "hub":
    replikator = multiprocessing.Process(
      target=modul_middleware.jalankan_replikator_proses,
      args=(saluran, INTI_REPLIKATOR, gerbang))
    replikator.start()

  daftar_proses = []
  for nomor in range(1, jumlah_unit + 1):
    proses = multiprocessing.Process(
      target=modul_unit.jalankan_unit_space_proses,
      args=(f"unit-{nomor}", nomor, messaging_grid, saluran, pump, pencatat,
            gerbang, KUOTA_UKUR, modul_unit.UKURAN_PENYANGGA_BAKU,
            INTI_UNIT[nomor - 1]))
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
  lama_simpan = time.monotonic() - mulai
  saluran.tutup()
  tersimpan = hitung_tersimpan()
  return {
    "lama_jawab": (selesai - mulai) * MILIDETIK,
    "lama_simpan": lama_simpan * MILIDETIK,
    "latensi": daftar_latensi,
    "dilayani": dilayani,
    "tersimpan": tersimpan,
  }


def jalankan_putaran_basis_data(jumlah_unit: int,
                                daftar_request: list) -> dict:
  """Menjalankan satu putaran versi basis data lalu mengukurnya.

  Kedua lajunya sama, sebab setiap request sudah tertulis sebelum dijawab.
  Mengembalikan dict berisi kedua laju per detik beserta daftar latensinya.
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
            basis_data.NAMA_BERKAS, INTI_UNIT[nomor - 1]))
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


def ulang_keadaan(nama: str, jumlah_unit: int, daftar_request: list) -> dict:
  """Menjalankan satu keadaan sebanyak PUTARAN kali lalu meringkasnya.

  Laju yang dilaporkan adalah median dari seluruh putaran, sedangkan latensi
  seluruh putaran digabung lebih dahulu agar sebarannya terbaca dari seluruh
  request, bukan dari satu putaran saja. Mengembalikan dict berisi ringkasan
  keadaan itu.
  """
  daftar_lama_jawab = []
  daftar_lama_simpan = []
  latensi_gabungan = []
  jumlah_baris = 0
  for _ in range(PUTARAN):
    if nama == "basis data":
      hasil = jalankan_putaran_basis_data(jumlah_unit, daftar_request)
    elif nama == "space":
      hasil = jalankan_putaran_space(jumlah_unit, daftar_request, "replikasi")
    elif nama == "space replikator":
      hasil = jalankan_putaran_space(jumlah_unit, daftar_request, "hub")
    else:
      hasil = jalankan_putaran_space(jumlah_unit, daftar_request, "senyap")
    daftar_lama_jawab.append(hasil["lama_jawab"])
    daftar_lama_simpan.append(hasil["lama_simpan"])
    latensi_gabungan.extend(hasil["latensi"])
    jumlah_baris = hasil["tersimpan"]
  lama_jawab = statistics.median(daftar_lama_jawab)
  lama_simpan = statistics.median(daftar_lama_simpan)
  return {
    "nama": nama,
    "unit": jumlah_unit,
    "lama_jawab": lama_jawab,
    "lama_simpan": lama_simpan,
    "dijawab_per_detik": JUMLAH_REQUEST / lama_jawab * MILIDETIK,
    "tersimpan_per_detik": jumlah_baris / lama_simpan * MILIDETIK,
    "jawab_terkecil": min(daftar_lama_jawab),
    "jawab_terbesar": max(daftar_lama_jawab),
    "sebaran": sebaran.ringkas(latensi_gabungan),
    "tersimpan": jumlah_baris,
  }


def cetak_judul_tabel() -> None:
  """Mencetak baris judul tabel hasil, sekali sebelum barisnya dicetak.

  Dua kolom pertama laju, yaitu banyaknya request yang selesai dalam satu
  detik. Dua kolom berikutnya lama seluruh beban, dan dua terakhir latensi
  satu request. Tidak mengembalikan apa pun.
  """
  print(f"{'Unit':>4} {'Keadaan':<21} {'Dijawab/detik':>13} "
        f"{'Tersimpan/detik':>15} {'Lama jawab ms':>13} "
        f"{'Lama simpan ms':>14} {'Latensi median':>14} {'Terbesar':>9}")


def cetak_baris(hasil: dict) -> None:
  """Mencetak satu baris hasil pengukuran dengan bentuk yang tetap.

  Labelnya memakai istilah yang sama dengan naskah bab, sebab langkah latihan
  menyuruh mahasiswa mencatat baris ini. Tidak mengembalikan apa pun.
  """
  ringkasan = hasil["sebaran"]
  print(f"{hasil['unit']:>4} {hasil['nama']:<21} "
        f"{hasil['dijawab_per_detik']:13.1f} "
        f"{hasil['tersimpan_per_detik']:15.1f} "
        f"{hasil['lama_jawab']:13.1f} {hasil['lama_simpan']:14.1f} "
        f"{ringkasan['median']:14.2f} {ringkasan['terbesar']:9.2f}")


def cetak_judul_ragam() -> None:
  """Mencetak baris judul tabel ragam antar putaran.

  Tidak mengembalikan apa pun.
  """
  print(f"{'Unit':>4} {'Keadaan':<21} {'Tercepat ms':>12} {'Median ms':>12} "
        f"{'Terlama ms':>12}")


def cetak_ragam(hasil: dict) -> None:
  """Mencetak sebaran lama dijawab antar putaran bagi satu keadaan.

  Selisih antar jumlah unit baru layak disebut ada bila lebih besar daripada
  jarak tercepat ke terlama di baris ini. Tidak mengembalikan apa pun.
  """
  print(f"{hasil['unit']:>4} {hasil['nama']:<21} "
        f"{hasil['jawab_terkecil']:12.1f} {hasil['lama_jawab']:12.1f} "
        f"{hasil['jawab_terbesar']:12.1f}")


def jalankan_satu_campuran(bagian_ambil: float, judul: str) -> list:
  """Menjalankan seluruh keadaan pada satu campuran beban lalu mencetaknya.

  Mengembalikan list berisi ringkasan tiap keadaan, berurutan menurut jumlah
  unit lalu menurut KEADAAN.
  """
  daftar_request = domain.bangkitkan_request(JUMLAH_REQUEST,
                                             bagian_ambil=bagian_ambil)
  jumlah_ambil = domain.hitung_ambil(daftar_request)
  print(f"\nBeban {judul}: {jumlah_ambil} dari {JUMLAH_REQUEST} request "
        f"mengambil kuota, sisanya membaca")
  cetak_judul_tabel()
  kumpulan = []
  for jumlah in JUMLAH_UNIT:
    baris_keadaan = []
    for nama_keadaan in KEADAAN:
      ringkasan_keadaan = ulang_keadaan(nama_keadaan, jumlah, daftar_request)
      cetak_baris(ringkasan_keadaan)
      baris_keadaan.append(ringkasan_keadaan)
    kumpulan.append(baris_keadaan)
  return kumpulan


def cetak_ringkasan_campuran(kumpulan: list) -> None:
  """Mencetak ragam antar putaran beserta perbandingan kedua versinya.

  Tidak mengembalikan apa pun.
  """
  print("\nRagam laju dijawab antar putaran:")
  cetak_judul_ragam()
  for baris_keadaan in kumpulan:
    for ringkasan_keadaan in baris_keadaan:
      cetak_ragam(ringkasan_keadaan)
  print()
  for baris_keadaan in kumpulan:
    hasil_basis, hasil_space, hasil_hub, hasil_senyap = baris_keadaan
    jawab = hasil_basis["lama_jawab"] / hasil_space["lama_jawab"]
    biaya = hasil_space["lama_jawab"] / hasil_senyap["lama_jawab"]
    tolong = hasil_space["lama_jawab"] / hasil_hub["lama_jawab"]
    print(f"Pada {hasil_basis['unit']} unit, space {jawab:5.1f} kali lebih "
          f"cepat daripada basis data, replikasi memperlambatnya {biaya:5.1f} "
          f"kali, dan replikator terpisah memperbaikinya {tolong:5.1f} kali")


if __name__ == "__main__":
  multiprocessing.set_start_method("spawn", force=True)
  print(f"Beban tiap keadaan : {JUMLAH_REQUEST} request serentak, "
        f"{PUTARAN} putaran")
  print(f"Kuota tiap kelas   : {KUOTA_UKUR} mahasiswa")
  print(f"Replication lag    : {JEDA_REPLIKASI * 1000:.0f} ms")
  print(f"Prosesor unit      : satu unit satu prosesor, yaitu CPU "
        f"{', '.join(str(inti) for inti in INTI_UNIT)}")
  print(f"Prosesor replikator: CPU {INTI_REPLIKATOR} saja, dipakai keadaan "
        f"space replikator")
  print("Pengirim beban     : tidak dikunci, sebab seluruh prosesor sudah "
        "terpakai unit dan replikator")
  print("Dijawab/detik   : banyaknya request yang selesai dijawab dalam satu "
        "detik.")
  print("Tersimpan/detik : banyaknya baris yang selesai ditulis ke basis data "
        "dalam satu detik.")
  print("Lama jawab      : sejak request masuk antrean sampai mahasiswa "
        "terakhir menerima jawaban.")
  print("Lama simpan     : sejak saat yang sama sampai baris terakhir "
        "tertulis di basis data.")
  print("Latensi         : sejak satu request masuk antrean sampai "
        "mahasiswanya dijawab.")

  batas_antrean = ukur_batas_antrean(domain.bangkitkan_request(JUMLAH_REQUEST))
  print(f"Batas messaging grid : {batas_antrean:.1f} ms untuk "
        f"{JUMLAH_REQUEST} request, yaitu tanpa pekerjaan apa pun di dalam "
        f"unit")

  for bagian, nama_campuran in CAMPURAN:
    hasil_campuran = jalankan_satu_campuran(bagian, nama_campuran)
    cetak_ringkasan_campuran(hasil_campuran)
