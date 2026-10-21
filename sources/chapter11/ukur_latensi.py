"""Mengukur tambahan waktu tanggap akibat pemanggilan lewat jaringan.

Permintaan yang diukur sama persis pada kedua versi, yaitu menerbitkan
tagihan untuk pesanan nomor satu. Permintaan itu menyentuh ketiga bidang
sekaligus, sehingga versi monolit menyelesaikannya dengan tiga pemanggilan
fungsi, sedangkan versi service-based menempuh tiga lompatan jaringan
tambahan.

Yang dilaporkan bukan rata-rata, melainkan median, persentil ke-95, dan nilai
terbesar. Gejala antrean hanya terlihat pada dua angka terakhir. Selisih
median juga dibandingkan dengan range di dalam jalur monolit, sebab selisih
yang lebih kecil daripada ragam pengukurannya sendiri belum dapat disebut
ada.

Cara menjalankan: python ukur_latensi.py
"""

import math
import statistics
import time

import requests

import alamat
import basis_data
import jalankan_layanan

JUMLAH_PUTARAN = 150
PUTARAN_PEMANASAN = 20
PUTARAN_PER_LAPORAN = 30
DETIK_KE_MILIDETIK = 1000.0
PERSENTIL = 95

# Permintaan gabungan, yaitu satu-satunya jenis permintaan yang menyentuh
# ketiga bidang domain sekaligus.
PERMINTAAN_UKUR = ("terbitkan tagihan", "POST", "/pesanan/1/tagihan")


def persentil(angka: list[float], peringkat: int) -> float:
  """Menghitung persentil memakai cara peringkat terdekat.

  Cara ini dipilih agar angka yang dilaporkan benar-benar salah satu hasil
  pengukuran, bukan hasil penafsiran antar dua pengukuran. Mengembalikan
  float berisi nilai pada persentil yang diminta.
  """
  urut = sorted(angka)
  letak = math.ceil(peringkat / 100 * len(urut)) - 1
  return urut[letak]


def satu_permintaan(sesi: requests.Session, porta: int) -> tuple[float, int]:
  """Mengirim satu permintaan gabungan lalu mencatat lama tanggapannya.

  Waktu dihitung sejak permintaan dikirim sampai jawabannya terbaca penuh,
  sehingga mencakup seluruh lompatan yang terjadi di dalam sistem.
  Mengembalikan tuple berisi float lama dalam milidetik dan int jumlah
  lompatan jaringan yang dilaporkan jawabannya.
  """
  _, metode, jalur = PERMINTAAN_UKUR
  tujuan = f"{alamat.alamat_dasar(porta)}{jalur}"
  mulai = time.perf_counter()
  jawaban = sesi.request(metode, tujuan, timeout=alamat.BATAS_WAKTU_DETIK)
  lama = (time.perf_counter() - mulai) * DETIK_KE_MILIDETIK
  return lama, jawaban.json()["lompatan"]


def panaskan(sesi: requests.Session) -> None:
  """Menjalankan beberapa putaran yang hasilnya sengaja dibuang.

  Permintaan pertama pada setiap proses menanggung penyiapan sambungan dan
  pembukaan berkas basis data, dan biaya itu hanya dibayar sekali. Tidak
  mengembalikan apa pun.
  """
  for _ in range(PUTARAN_PEMANASAN):
    satu_permintaan(sesi, alamat.PORTA_MONOLIT)
    satu_permintaan(sesi, alamat.PORTA_GERBANG)


def jalankan_putaran(sesi: requests.Session) -> tuple[list, list, dict]:
  """Mengukur kedua versi bergantian sebanyak putaran yang diminta.

  Keduanya diukur di dalam putaran yang sama agar menghadapi keadaan mesin
  yang serupa, sebab kesibukan laptop berubah dari menit ke menit.
  Mengembalikan tuple berisi dua list waktu dan satu dict jumlah lompatan
  tiap versi.
  """
  monolit, layanan = [], []
  lompatan = {}
  mulai = time.perf_counter()
  print(f"Menjalankan {JUMLAH_PUTARAN} putaran pada kedua versi.", flush=True)
  for nomor in range(1, JUMLAH_PUTARAN + 1):
    lama_monolit, lompatan["monolit"] = satu_permintaan(
      sesi, alamat.PORTA_MONOLIT)
    lama_layanan, lompatan["layanan"] = satu_permintaan(
      sesi, alamat.PORTA_GERBANG)
    monolit.append(lama_monolit)
    layanan.append(lama_layanan)
    if nomor % PUTARAN_PER_LAPORAN == 0:
      lewat = time.perf_counter() - mulai
      sisa = lewat / nomor * (JUMLAH_PUTARAN - nomor)
      print(f"  putaran {nomor:3d}/{JUMLAH_PUTARAN}"
            f"  monolit {statistics.median(monolit):5.1f} ms"
            f"  service-based {statistics.median(layanan):5.1f} ms"
            f"  sisa sekitar {sisa:3.0f} detik", flush=True)
  return monolit, layanan, lompatan


def laporkan(monolit: list, layanan: list, lompatan: dict) -> None:
  """Mencetak laporan akhir pengukuran dalam bentuk yang siap disalin.

  Label yang dicetak sama dengan istilah pada naskah bab, sebab langkah
  latihan menyuruh mahasiswa menyalin baris keluaran ini ke dalam tabel.
  Tidak mengembalikan apa pun.
  """
  median_monolit = statistics.median(monolit)
  median_layanan = statistics.median(layanan)
  selisih = median_layanan - median_monolit
  range_monolit = max(monolit) - min(monolit)
  menang = sum(1 for satu, dua in zip(monolit, layanan) if satu < dua)

  print(f"Putaran                       : {JUMLAH_PUTARAN}")
  print(f"Median monolit                : {median_monolit:.2f} ms")
  print(f"Median service-based          : {median_layanan:.2f} ms")
  print(f"Persentil ke-95 monolit       : "
        f"{persentil(monolit, PERSENTIL):.2f} ms")
  print(f"Persentil ke-95 service-based : "
        f"{persentil(layanan, PERSENTIL):.2f} ms")
  print(f"Terbesar monolit              : {max(monolit):.2f} ms")
  print(f"Terbesar service-based        : {max(layanan):.2f} ms")
  print(f"Selisih median                : {selisih:.2f} ms")
  print(f"Service-based lebih lambat    : {median_layanan / median_monolit:.1f}"
        " kali")
  print(f"Range dalam jalur monolit     : {range_monolit:.2f} ms")
  print(f"Range dibagi selisih          : {range_monolit / selisih:.2f} kali")
  print(f"Putaran monolit lebih cepat   : {menang} dari {JUMLAH_PUTARAN}")
  print(f"Lompatan monolit              : {lompatan['monolit']}")
  print(f"Lompatan service-based        : {lompatan['layanan']}")


if __name__ == "__main__":
  basis_data.siapkan()
  proses_hidup = jalankan_layanan.nyalakan({
    **jalankan_layanan.PROSES_MONOLIT,
    **jalankan_layanan.PROSES_LAYANAN,
  })
  sesi_klien = requests.Session()
  try:
    panaskan(sesi_klien)
    hasil_monolit, hasil_layanan, jumlah_lompatan = jalankan_putaran(
      sesi_klien)
    laporkan(hasil_monolit, hasil_layanan, jumlah_lompatan)
    # Keluarannya: Putaran monolit lebih cepat   : 150 dari 150
  finally:
    sesi_klien.close()
    jalankan_layanan.matikan(proses_hidup)
