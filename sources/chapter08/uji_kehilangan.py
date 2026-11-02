"""Menguji data loss, yaitu jawaban yang sudah terlanjur diberikan lalu lenyap.

Request dikirim dengan laju tetap, seperti mahasiswa yang berdatangan sepanjang
jam pengisian, lalu satu processing unit dimatikan di tengah jalan. Pada versi
basis data, setiap request sudah tertulis sebelum dijawab, sehingga yang hilang
paling banyak satu request yang sedang berjalan. Pada versi space, perubahan
yang masih tertahan di penyangga unit ikut mati bersamanya, padahal mahasiswa
sudah menerima jawaban.

Yang dilaporkan selisih antara jumlah request yang dijawab dan jumlah baris
yang benar-benar tersimpan. Selisih itulah harga yang dibayar karena
penyimpanan dikeluarkan dari jalur request.

Cara menjalankan: python uji_kehilangan.py
"""

import time

import basis_data
import domain
import middleware as modul_middleware
import sebaran
import unit as modul_unit

# Banyaknya request pada setiap putaran.
JUMLAH_REQUEST = 6000
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
# Ukuran penyangga unit pada versi space, yaitu perubahan yang ditahan di
# memori sebelum diserahkan kepada data pump.
UKURAN_PENYANGGA = 50


def kirim_berjadwal(messaging_grid, daftar_request: list, aksi_mati) -> int:
  """Mengirim request dengan laju tetap lalu mematikan satu unit di tengahnya.

  Laju tetap dipakai agar kedua versi menerima beban yang sama bentuknya, dan
  agar unit yang dimatikan benar-benar sedang bekerja. Mengembalikan int berisi
  jumlah perubahan yang lenyap bersama unit itu.
  """
  jeda = 1.0 / LAJU_KEDATANGAN
  batas_mati = int(len(daftar_request) * BAGIAN_MATI)
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


def jalankan_versi_space(daftar_request: list) -> dict:
  """Menjalankan versi space lalu mematikan satu unit di tengah beban.

  Mengembalikan dict berisi request yang dijawab, baris yang tersimpan,
  selisih keduanya, dan jumlah yang tertahan di penyangga saat unit mati.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid, daftar_unit, pump, writer, saluran = \
    modul_unit.rakit_versi_space(JUMLAH_UNIT, JEDA_REPLIKASI,
                                 basis_data.NAMA_BERKAS, KUOTA_UKUR,
                                 UKURAN_PENYANGGA)
  writer.mulai()
  for unit in daftar_unit:
    unit.mulai()

  hilang_penyangga = kirim_berjadwal(messaging_grid, daftar_request,
                                     daftar_unit[0].mati)
  time.sleep(0.3)
  dijawab = sum(unit.jumlah_dilayani for unit in daftar_unit)
  for unit in daftar_unit[1:]:
    unit.hentikan()
  writer.hentikan()
  saluran.tutup()

  basis = basis_data.BasisData()
  tersimpan = basis.jumlah_pengambilan()
  basis.tutup()
  return {
    "versi": "space",
    "dijawab": dijawab,
    "tersimpan": tersimpan,
    "hilang": dijawab - tersimpan,
    "hilang_penyangga": hilang_penyangga,
  }


def jalankan_versi_basis_data(daftar_request: list) -> dict:
  """Menjalankan versi basis data lalu mematikan satu unit di tengah beban.

  Mengembalikan dict berisi request yang dijawab, baris yang tersimpan, dan
  selisih keduanya.
  """
  basis_data.siapkan_berkas_baru(per_kelas=KUOTA_UKUR)
  messaging_grid = modul_middleware.MessagingGrid()
  daftar_unit = []
  for nomor in range(1, JUMLAH_UNIT + 1):
    daftar_unit.append(modul_unit.UnitBasisData(
      f"unit-{nomor}", messaging_grid, basis_data.NAMA_BERKAS))
  for unit in daftar_unit:
    unit.mulai()

  kirim_berjadwal(messaging_grid, daftar_request, daftar_unit[0].mati)
  time.sleep(0.5)
  dijawab = sum(unit.jumlah_dilayani for unit in daftar_unit)
  for unit in daftar_unit[1:]:
    unit.hentikan()

  basis = basis_data.BasisData()
  tersimpan = basis.jumlah_pengambilan()
  basis.tutup()
  return {
    "versi": "basis data",
    "dijawab": dijawab,
    "tersimpan": tersimpan,
    "hilang": dijawab - tersimpan,
    "hilang_penyangga": 0,
  }


if __name__ == "__main__":
  daftar_request_utama = domain.bangkitkan_request(JUMLAH_REQUEST)
  print(f"Beban tiap putaran     : {JUMLAH_REQUEST} request, "
        f"{LAJU_KEDATANGAN} per detik")
  print(f"Processing unit        : {JUMLAH_UNIT}, satu dimatikan pada "
        f"{BAGIAN_MATI * 100:.0f} persen beban")
  print(f"Penyangga unit         : {UKURAN_PENYANGGA} perubahan\n")

  hilang_basis = []
  hilang_space = []
  print(f"{'Putaran':>8}{'Hilang, basis data':>22}{'Hilang, space':>18}"
        f"{'Tertahan penyangga':>22}")
  for putaran in range(1, PUTARAN + 1):
    hasil_basis = jalankan_versi_basis_data(daftar_request_utama)
    hasil_space = jalankan_versi_space(daftar_request_utama)
    hilang_basis.append(hasil_basis["hilang"])
    hilang_space.append(hasil_space["hilang"])
    print(f"{putaran:>8}{hasil_basis['hilang']:>22}"
          f"{hasil_space['hilang']:>18}"
          f"{hasil_space['hilang_penyangga']:>22}")

  ringkas_basis = sebaran.ringkas(hilang_basis)
  ringkas_space = sebaran.ringkas(hilang_space)
  print(f"\nMedian hilang, basis data : {ringkas_basis['median']:.0f} request")
  print(f"Median hilang, space      : {ringkas_space['median']:.0f} request")
  print(f"Terbesar hilang, space    : {ringkas_space['terbesar']:.0f} request")
  putaran_hilang = sum(1 for angka in hilang_space if angka > 0)
  print(f"Putaran yang kehilangan   : {putaran_hilang} dari {PUTARAN}")
