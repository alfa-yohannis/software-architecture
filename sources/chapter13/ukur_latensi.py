"""Mengukur latensi dan jumlah lompatan pada versi monolit dan mikroservis.

Dua jalur diukur pada kedua versi. Jalur nasabah hanya menyentuh satu sumber
data, sehingga selisihnya memperlihatkan biaya satu lompatan tambahan yang
murni. Jalur laporan menyentuh tiga sumber data sekaligus, sehingga selisihnya
memperlihatkan biaya pemisahan basis data.

Kedua versi dinyalakan berbarengan pada porta yang berbeda, lalu diukur
bergantian di dalam putaran yang sama. Cara itu dipakai sebab mesin yang sedang
sibuk mengerjakan hal lain membuat angka mutlaknya naik turun, sedangkan
perbandingan di dalam satu putaran tetap sah. Selain sebarannya, dilaporkan pula
berapa kali tiap versi menang, sebab pencacahan per putaran lebih tahan terhadap
satu putaran yang melonjak.

Cara menjalankan: python ukur_latensi.py
"""

import statistics
import time

import requests

import alamat
import penjalan

JUMLAH_PUTARAN = 200
PUTARAN_PEMANASAN = 20
PUTARAN_PER_LAPORAN = 50
TENGGANG_DETIK = 5.0
DETIK_KE_MILIDETIK = 1000.0
PERSEN_PERSENTIL = 0.95

JALUR = {
  "nasabah": "/nasabah/N-001",
  "laporan": "/laporan/N-001",
}

VERSI = {
  "monolit": alamat.MONOLIT,
  "mikroservis": alamat.GERBANG,
}

SESI = requests.Session()


def persentil_95(nilai: list[float]) -> float:
  """Mengambil nilai pada peringkat ke-95 persen dari daftar yang sudah diurut.

  Cara peringkat terdekat dipakai agar angkanya benar-benar salah satu hasil
  pengukuran, bukan hasil interpolasi yang tidak pernah terjadi. Mengembalikan
  float berisi persentil ke-95 dalam satuan yang sama dengan masukannya.
  """
  urut = sorted(nilai)
  posisi = max(0, round(PERSEN_PERSENTIL * len(urut)) - 1)
  return urut[posisi]


def satu_permintaan(url: str) -> tuple[float, int]:
  """Mengirim satu permintaan lalu mencatat lamanya beserta jumlah lompatannya.

  Waktu dihitung dari sisi klien, sehingga sudah memuat seluruh lompatan di
  dalamnya. Mengembalikan tuple berisi float lama dalam milidetik dan int
  jumlah lompatan yang dilaporkan pelayannya.
  """
  mulai = time.perf_counter()
  jawaban = SESI.get(url, timeout=TENGGANG_DETIK)
  lama = (time.perf_counter() - mulai) * DETIK_KE_MILIDETIK
  return lama, jawaban.json()["lompatan"]


def panaskan() -> None:
  """Mengirim permintaan pendahuluan ke seluruh jalur pada kedua versi.

  Permintaan pertama menanggung pembuatan sambungan TCP dan penyiapan cache
  basis data, sehingga angkanya tidak mewakili keadaan biasa. Fungsi ini tidak
  mengembalikan nilai.
  """
  for _ in range(PUTARAN_PEMANASAN):
    for induk in VERSI.values():
      for jalur in JALUR.values():
        satu_permintaan(induk + jalur)


def jalankan_putaran() -> tuple[dict, dict]:
  """Mengukur seluruh gabungan versi dan jalur bergantian di tiap putaran.

  Urutannya sengaja versi dahulu lalu jalur, sehingga kedua versi selalu diukur
  berdekatan dan menghadapi keadaan mesin yang serupa. Mengembalikan tuple
  berisi dict daftar waktu dan dict jumlah lompatan, keduanya berkunci pasangan
  nama versi dan nama jalur.
  """
  waktu = {(versi, jalur): [] for versi in VERSI for jalur in JALUR}
  lompatan = {}
  mulai = time.perf_counter()
  print(f"Menjalankan {JUMLAH_PUTARAN} putaran pada kedua versi.", flush=True)
  for nomor in range(1, JUMLAH_PUTARAN + 1):
    for nama_jalur, jalur in JALUR.items():
      for nama_versi, induk in VERSI.items():
        lama, cacah = satu_permintaan(induk + jalur)
        waktu[(nama_versi, nama_jalur)].append(lama)
        lompatan[(nama_versi, nama_jalur)] = cacah
    if nomor % PUTARAN_PER_LAPORAN == 0:
      lewat = time.perf_counter() - mulai
      print(f"  putaran {nomor:3d}/{JUMLAH_PUTARAN}"
            f"  laporan monolit {statistics.median(waktu[('monolit', 'laporan')]):6.2f} ms"
            f"  laporan mikroservis"
            f" {statistics.median(waktu[('mikroservis', 'laporan')]):6.2f} ms"
            f"  lewat {lewat:4.0f} detik", flush=True)
  return waktu, lompatan


def cetak_baris(nama_versi: str, nama_jalur: str, waktu: dict,
                lompatan: dict) -> None:
  """Mencetak satu baris laporan berisi sebaran latensi dan jumlah lompatan.

  Susunan kolomnya dibuat sama dengan susunan tabel pada naskah bab, sehingga
  angkanya tinggal disalin. Fungsi ini tidak mengembalikan nilai.
  """
  nilai = waktu[(nama_versi, nama_jalur)]
  print(f"{nama_versi:<12} {nama_jalur:<9}"
        f" {statistics.median(nilai):8.2f}"
        f" {persentil_95(nilai):8.2f}"
        f" {max(nilai):9.2f}"
        f" {lompatan[(nama_versi, nama_jalur)]:9d}")


if __name__ == "__main__":
  berjalan = penjalan.nyalakan(penjalan.NAMA_MONOLIT + penjalan.NAMA_MIKROSERVIS)
  try:
    panaskan()
    hasil_waktu, hasil_lompatan = jalankan_putaran()
  finally:
    penjalan.matikan(berjalan)

  print(f"\nPutaran per jalur : {JUMLAH_PUTARAN}")
  print(f"{'Versi':<12} {'Permintaan':<9} {'Median':>8} {'p95':>8}"
        f" {'Terbesar':>9} {'Lompatan':>9}")
  for nama_versi_cetak in VERSI:
    for nama_jalur_cetak in JALUR:
      cetak_baris(nama_versi_cetak, nama_jalur_cetak, hasil_waktu, hasil_lompatan)

  print()
  for nama_jalur_cetak in JALUR:
    monolit = hasil_waktu[("monolit", nama_jalur_cetak)]
    mikro = hasil_waktu[("mikroservis", nama_jalur_cetak)]
    menang = sum(1 for satu, dua in zip(monolit, mikro) if satu < dua)
    print(f"Jalur {nama_jalur_cetak:<8} monolit lebih cepat :"
          f" {menang:3d} dari {JUMLAH_PUTARAN},"
          f" selisih median {statistics.median(mikro) - statistics.median(monolit):6.2f} ms,"
          f" {statistics.median(mikro) / statistics.median(monolit):.1f} kali")
  # Keluarannya baris kedua: Jalur laporan  monolit lebih cepat : 200 dari 200
