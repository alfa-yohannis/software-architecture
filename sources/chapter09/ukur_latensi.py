"""Membandingkan latensi ketiga susunan pada pekerjaan yang sama persis.

Dua waktu diukur pada setiap permintaan. Waktu penerbit kembali dihitung sejak
permintaan dikirim sampai fungsi kirim() kembali, sedangkan latensi ujung ke
ujung dihitung sampai langkah terakhir selesai. Pada susunan sinkron keduanya
hampir sama, sebab pemanggil memang menunggu seluruh pekerjaan.

Ketiga susunan diukur berselang-seling di dalam putaran yang sama, bukan
berurutan satu demi satu. Cara itu dipilih agar beban mesin yang berubah di
tengah pengukuran menimpa ketiganya sekaligus, sehingga pencacahan kemenangan
per putaran tetap sah. Yang dilaporkan adalah median, persentil ke-95, nilai
terbesar, dan pencacahan itu.

Cara menjalankan: python ukur_latensi.py
"""

import math
import statistics
import time

import broker
import domain
import mediator
import sinkron

JUMLAH_PERMINTAAN = 200
JUMLAH_PEMANASAN = 20
BATAS_TUNGGU = 5.0
MILIDETIK = 1000.0
PERINGKAT_PERSENTIL = 95
PERMINTAAN_PER_LAPORAN = 50

# Ketiga susunan yang dibandingkan, beserta fungsi perakitnya. Urutannya
# sengaja dimulai dari susunan tanpa event, sebab susunan itulah titik nolnya.
SUSUNAN = (
  ("sinkron", sinkron.rakit),
  ("broker", broker.rakit),
  ("mediator", mediator.rakit),
)
NAMA_DASAR = SUSUNAN[0][0]


def persentil(daftar: list, peringkat: int) -> float:
  """Mengembalikan float nilai persentil dengan cara peringkat terdekat.

  Cara ini dipilih karena tidak menyisipkan nilai baru di antara dua
  pengukuran, sehingga angka yang dilaporkan benar-benar pernah terjadi.
  """
  terurut = sorted(daftar)
  posisi = math.ceil(peringkat / 100 * len(terurut)) - 1
  return terurut[max(0, min(posisi, len(terurut) - 1))]


def ukur_satu(susunan, nomor: int) -> tuple:
  """Mengirim satu permintaan lalu mengukur kedua waktunya.

  Mengembalikan tuple berisi waktu penerbit kembali, latensi ujung ke ujung,
  keduanya dalam milidetik, beserta bool penanda permintaan itu tuntas.
  """
  permintaan = domain.buat_permintaan(nomor, susunan.jumlah_langkah())
  mulai = time.perf_counter()
  susunan.kirim(permintaan)
  kembali = time.perf_counter()
  tuntas = permintaan.tunggu(BATAS_TUNGGU)
  akhir = time.perf_counter()
  return ((kembali - mulai) * MILIDETIK, (akhir - mulai) * MILIDETIK, tuntas)


def panaskan(susunan) -> None:
  """Menjalankan permintaan pembuka agar thread dan cache impor sudah siap."""
  for nomor in range(1, JUMLAH_PEMANASAN + 1):
    ukur_satu(susunan, nomor)


def laporkan_kemajuan(nomor: int, catatan: dict) -> None:
  """Mencetak satu baris kemajuan berisi median sementara ketiga susunan."""
  bagian = [f"{nama} {statistics.median(isi['ujung']):.4f} ms"
            for nama, isi in catatan.items()]
  print(f"  putaran {nomor:3d}/{JUMLAH_PERMINTAAN}  " + "  ".join(bagian),
        flush=True)


def jalankan_pengukuran() -> tuple:
  """Menjalankan seluruh putaran pada ketiga susunan secara berselang-seling.

  Mengembalikan tuple berisi dict catatan waktu setiap susunan dan dict jumlah
  pesan setiap susunan selama pengukuran berlangsung.
  """
  susunan = {nama: perakit() for nama, perakit in SUSUNAN}
  catatan = {nama: {"kembali": [], "ujung": [], "tuntas": 0}
             for nama in susunan}
  for satu in susunan.values():
    panaskan(satu)
  pesan_awal = {nama: satu.pesan_terkirim() for nama, satu in susunan.items()}
  print(f"Menjalankan {JUMLAH_PERMINTAAN} putaran pada {len(susunan)} susunan.",
        flush=True)
  for nomor in range(1, JUMLAH_PERMINTAAN + 1):
    for nama, satu in susunan.items():
      waktu_kembali, waktu_ujung, tuntas = ukur_satu(satu, nomor)
      catatan[nama]["kembali"].append(waktu_kembali)
      catatan[nama]["ujung"].append(waktu_ujung)
      if tuntas:
        catatan[nama]["tuntas"] += 1
    if nomor % PERMINTAAN_PER_LAPORAN == 0:
      laporkan_kemajuan(nomor, catatan)
  pesan = {nama: satu.pesan_terkirim() - pesan_awal[nama]
           for nama, satu in susunan.items()}
  for satu in susunan.values():
    satu.tutup()
  return catatan, pesan


def rangkum(nama: str, catatan: dict, pesan: int) -> dict:
  """Merangkum catatan satu susunan menjadi angka yang siap dicetak.

  Mengembalikan dict berisi median, persentil ke-95, nilai terbesar, range,
  median waktu penerbit kembali, pesan per permintaan, dan jumlah yang tuntas.
  """
  ujung = catatan["ujung"]
  kembali = catatan["kembali"]
  return {
    "nama": nama,
    "median": statistics.median(ujung),
    "persentil": persentil(ujung, PERINGKAT_PERSENTIL),
    "terbesar": max(ujung),
    "range_ujung": max(ujung) - min(ujung),
    "kembali": statistics.median(kembali),
    "range_kembali": max(kembali) - min(kembali),
    "pesan": pesan / JUMLAH_PERMINTAAN,
    "tuntas": catatan["tuntas"],
  }


def hitung_menang(kiri: list, kanan: list) -> int:
  """Mengembalikan int jumlah putaran ketika nilai kiri lebih kecil.

  Pencacahan per putaran dipakai sebab jauh lebih tahan terhadap satu putaran
  ganjil daripada range, yang seluruhnya ditentukan dua nilai ekstrem.
  """
  return sum(1 for a, b in zip(kiri, kanan) if a < b)


def cetak_ringkasan(hasil: list) -> None:
  """Mencetak tabel ringkasan ketiga susunan dengan satuan yang seragam."""
  print(f"\nPermintaan per susunan       : {JUMLAH_PERMINTAAN}")
  print("Seluruh waktu dalam milidetik, pesan dihitung per permintaan.\n")
  print(f"{'Susunan':<10}{'Median':>10}{'Persentil-95':>14}{'Terbesar':>10}"
        f"{'Kembali':>10}{'Pesan':>8}{'Tuntas':>8}")
  for baris in hasil:
    print(f"{baris['nama']:<10}{baris['median']:>10.4f}"
          f"{baris['persentil']:>14.4f}{baris['terbesar']:>10.4f}"
          f"{baris['kembali']:>10.4f}{baris['pesan']:>8.1f}"
          f"{baris['tuntas']:>8d}")


def cetak_perbandingan(hasil: list, catatan: dict) -> None:
  """Membandingkan kedua susunan berbasis event terhadap susunan sinkron.

  Setiap selisih median dibandingkan dengan range di dalam jalur sinkron, lalu
  ditegaskan dengan pencacahan kemenangan per putaran. Kedua ukuran itu dicetak
  bersama-sama, sebab keduanya dapat menunjuk arah yang berbeda.
  """
  dasar = hasil[0]
  catatan_dasar = catatan[NAMA_DASAR]
  print(f"\nRange ujung ke ujung sinkron  : {dasar['range_ujung']:.4f} ms")
  print(f"Range penerbit kembali sinkron: {dasar['range_kembali']:.4f} ms")
  for baris in hasil[1:]:
    nama = baris["nama"]
    selisih_ujung = baris["median"] - dasar["median"]
    selisih_kembali = dasar["kembali"] - baris["kembali"]
    menang_ujung = hitung_menang(catatan_dasar["ujung"], catatan[nama]["ujung"])
    menang_kembali = hitung_menang(catatan[nama]["kembali"],
                                   catatan_dasar["kembali"])
    print(f"\nUjung ke ujung {nama} dibanding sinkron")
    print(f"  median lebih besar          : "
          f"{baris['median'] / dasar['median']:.1f} kali")
    print(f"  selisih median              : {selisih_ujung:.4f} ms")
    print(f"  range sinkron dibagi selisih: "
          f"{dasar['range_ujung'] / selisih_ujung:.1f} kali")
    print(f"  putaran sinkron lebih cepat : {menang_ujung} dari "
          f"{JUMLAH_PERMINTAAN}")
    print(f"Penerbit kembali {nama} dibanding sinkron")
    print(f"  selisih median              : {selisih_kembali:.4f} ms")
    print(f"  range sinkron dibagi selisih: "
          f"{dasar['range_kembali'] / abs(selisih_kembali):.1f} kali")
    print(f"  putaran event lebih cepat   : {menang_kembali} dari "
          f"{JUMLAH_PERMINTAAN}")


if __name__ == "__main__":
  mulai_seluruh = time.perf_counter()
  catatan_waktu, jumlah_pesan = jalankan_pengukuran()
  laporan = [rangkum(nama, catatan_waktu[nama], jumlah_pesan[nama])
             for nama, _ in SUSUNAN]
  cetak_ringkasan(laporan)
  cetak_perbandingan(laporan, catatan_waktu)
  # Keluarannya: putaran sinkron lebih cepat : 200 dari 200
  print(f"\nSeluruh pengukuran selesai dalam "
        f"{(time.perf_counter() - mulai_seluruh) * MILIDETIK:.0f} ms.")
