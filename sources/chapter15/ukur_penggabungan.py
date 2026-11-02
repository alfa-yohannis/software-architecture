"""Mengukur lama tahap penggabungan peringkat pada jalur panas pencarian Exim.

Tahap ini berjalan pada setiap pertanyaan, sesudah pencarian vektor dan
pencarian kata kunci selesai, lalu sebelum cross-encoder dijalankan. Karena
tidak menyentuh jaringan maupun korpus, tahap ini dapat diukur di laptop mana
pun, sehingga cocok menjadi keadaan awal sebuah makalah.

Yang diubah hanya jumlah kandidat yang masuk, sebab angka itulah yang
ditetapkan setelan dense_candidate_count dan sparse_candidate_count pada Exim.
Pengukurannya diulang ratusan kali, lalu yang dilaporkan median, persentil
ke-95, dan nilai terbesar. Satu kali pengukuran tidak cukup, sebab selisih yang
dicari lebih kecil daripada ragam satu putaran.

Cara menjalankan: python ukur_penggabungan.py
"""

import random
import time

import sebaran
import tahap_penggabungan

MIKRODETIK = 1000000.0
# Banyaknya putaran tiap keadaan. Angkanya besar sebab yang diukur hanya
# puluhan mikrodetik, sehingga ragam satu putaran mudah menutupi selisihnya.
PUTARAN = 500
# Jumlah kandidat tiap daftar yang dicoba. Nilai 50 adalah setelan bawaan
# Exim untuk kedua daftar, sedangkan nilai lain dipakai melihat arah biayanya.
JUMLAH_KANDIDAT = (10, 25, 50, 100, 200)
# Bagian kandidat yang sengaja dibuat muncul di kedua daftar, sehingga
# penggabungan benar-benar menjumlahkan sumbangan, bukan sekadar menyalin.
BAGIAN_BERIMPIT = 0.3
# Benih tetap agar daftar kandidat sama pada setiap penjalanan.
BENIH_BAKU = 2026


def bangkitkan_dua_daftar(jumlah: int, benih: int) -> tuple:
  """Menyusun sepasang daftar kandidat yang sebagiannya berimpit.

  Daftar pertama meniru hasil pencarian vektor, daftar kedua meniru hasil
  pencarian kata kunci. Sebagian chunk_id sengaja muncul di keduanya, persis
  seperti potongan yang ditemukan kedua metode sekaligus. Mengembalikan tuple
  berisi kedua list Potongan.
  """
  pengacak = random.Random(benih)
  jumlah_berimpit = int(jumlah * BAGIAN_BERIMPIT)
  daftar_vektor = []
  daftar_kata = []
  for nomor in range(jumlah):
    daftar_vektor.append(tahap_penggabungan.Potongan(
      nomor, skor_vektor=pengacak.random()))
  for nomor in range(jumlah):
    if nomor < jumlah_berimpit:
      chunk_id = nomor
    else:
      chunk_id = jumlah + nomor
    daftar_kata.append(tahap_penggabungan.Potongan(
      chunk_id, skor_kata=pengacak.random()))
  return daftar_vektor, daftar_kata


def salin_daftar(daftar: list) -> list:
  """Menyalin daftar kandidat agar putaran berikutnya berangkat dari nol.

  Penggabungan mengubah skor_gabungan di dalam objeknya, sehingga objek yang
  sama tidak boleh dipakai dua kali. Mengembalikan list berisi Potongan baru.
  """
  salinan = []
  for potongan in daftar:
    salinan.append(tahap_penggabungan.Potongan(
      potongan.chunk_id, potongan.skor_vektor, potongan.skor_kata))
  return salinan


def jalankan_satu_keadaan(jumlah_kandidat: int) -> dict:
  """Mengukur lama penggabungan pada satu jumlah kandidat.

  Mengembalikan dict berisi jumlah kandidat masuk, jumlah kandidat keluar, dan
  sebaran lama penggabungan dalam mikrodetik.
  """
  daftar_vektor, daftar_kata = bangkitkan_dua_daftar(jumlah_kandidat,
                                                     BENIH_BAKU)
  daftar_lama = []
  jumlah_keluar = 0
  for _ in range(PUTARAN):
    salinan_vektor = salin_daftar(daftar_vektor)
    salinan_kata = salin_daftar(daftar_kata)
    mulai = time.perf_counter()
    hasil = tahap_penggabungan.gabungkan_peringkat(
      [salinan_vektor, salinan_kata])
    daftar_lama.append((time.perf_counter() - mulai) * MIKRODETIK)
    jumlah_keluar = len(hasil)
  return {
    "masuk": jumlah_kandidat * 2,
    "keluar": jumlah_keluar,
    "sebaran": sebaran.ringkas(daftar_lama),
  }


if __name__ == "__main__":
  print(f"Putaran tiap keadaan : {PUTARAN}")
  print(f"Konstanta peredam    : {tahap_penggabungan.KONSTANTA_PEREDAM}")
  print(f"Bagian berimpit      : {BAGIAN_BERIMPIT * 100:.0f} persen\n")
  print(f"{'Kandidat masuk':>15}{'Kandidat keluar':>17}{'Median us':>12}"
        f"{'P95 us':>10}{'Terbesar us':>14}")
  for jumlah_utama in JUMLAH_KANDIDAT:
    hasil_utama = jalankan_satu_keadaan(jumlah_utama)
    ringkasan_utama = hasil_utama["sebaran"]
    print(f"{hasil_utama['masuk']:>15}{hasil_utama['keluar']:>17}"
          f"{ringkasan_utama['median']:>12.2f}{ringkasan_utama['p95']:>10.2f}"
          f"{ringkasan_utama['terbesar']:>14.2f}")
