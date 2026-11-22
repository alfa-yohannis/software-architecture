"""Mengukur latensi dan jumlah hop jaringan kedua versi workflow.

Kedua versi menjalankan workflow pemesanan valuta asing yang sama persis,
dengan enam langkah dan hasil akhir yang sama. Yang berbeda hanya cara
merangkainya. Versi orkestrasi mengembalikan konteks ke engine sesudah setiap
langkah, sedangkan versi tanpa orkestrasi meneruskannya langsung ke layanan
berikutnya.

Hop jaringan tidak diperkirakan, melainkan dihitung. Setiap layanan dan
orchestration engine menambah satu pencacah bersama ketika melayani satu request
HTTP, lalu pencacah itu dibaca sesudah satu workflow selesai.

Kedua versi dijalankan bergantian pada setiap putaran, agar keduanya menghadapi
kondisi komputer yang sama.

Cara menjalankan: python ukur_lompatan.py
"""

import statistics
import time

import data
import klien
import server

JUMLAH_PUTARAN = 200
PUTARAN_PEMANASAN = 5
PUTARAN_PER_LAPORAN = 40
MILIDETIK = 1000.0


def persentil(nilai: list, bagian: float) -> float:
  """Mengambil nilai pada persentil tertentu dari daftar yang belum terurut.

  Persentil ke-95 dipakai bab ini sebab gejala antrean tidak tampak pada
  median. Mengembalikan float berisi nilai pada persentil yang diminta.
  """
  urut = sorted(nilai)
  indeks = min(len(urut) - 1, int(round(bagian * (len(urut) - 1))))
  return urut[indeks]


def ukur_orkestrasi() -> tuple:
  """Menjalankan satu workflow lewat orchestration engine lalu mengukurnya.

  Mengembalikan tuple berisi float lama pemrosesan dalam milidetik dan int
  jumlah request HTTP yang dilayani.
  """
  data.nolkan_pencacah()
  mulai = time.perf_counter()
  klien.jalankan_orkestrasi("pesan-valas")
  lama = (time.perf_counter() - mulai) * MILIDETIK
  return lama, data.baca_pencacah()


def ukur_berantai() -> tuple:
  """Menjalankan satu workflow lewat rantai layanan lalu mengukurnya.

  Mengembalikan tuple berisi float lama pemrosesan dalam milidetik dan int
  jumlah request HTTP yang dilayani.
  """
  data.nolkan_pencacah()
  mulai = time.perf_counter()
  klien.jalankan_berantai()
  lama = (time.perf_counter() - mulai) * MILIDETIK
  return lama, data.baca_pencacah()


def panaskan() -> None:
  """Menjalankan beberapa workflow pembuka sebelum pengukuran dimulai.

  Putaran pertama selalu lebih mahal, sebab koneksi HTTP dan cache Flask belum
  terbentuk. Tidak mengembalikan nilai.
  """
  for _ in range(PUTARAN_PEMANASAN):
    ukur_orkestrasi()
    ukur_berantai()


def laporkan_kemajuan(nomor: int, orkestrasi: list, berantai: list,
                      mulai: float) -> None:
  """Mencetak satu baris kemajuan beserta perkiraan sisa waktunya.

  Tidak mengembalikan nilai.
  """
  lewat = time.perf_counter() - mulai
  sisa = lewat / nomor * (JUMLAH_PUTARAN - nomor)
  print(f"  putaran {nomor:3d}/{JUMLAH_PUTARAN}"
        f"  orkestrasi {statistics.median(orkestrasi):.3f} ms"
        f"  berantai {statistics.median(berantai):.3f} ms"
        f"  sisa sekitar {sisa:3.0f} detik", flush=True)


def jalankan_putaran() -> tuple:
  """Menjalankan kedua versi bergantian sebanyak putaran yang diminta.

  Mengembalikan tuple berisi dua list latensi dan dua int jumlah hop.
  """
  orkestrasi, berantai = [], []
  hop_orkestrasi, hop_berantai = 0, 0
  mulai = time.perf_counter()
  print(f"Menjalankan {JUMLAH_PUTARAN} workflow untuk kedua versi.",
        flush=True)
  for nomor in range(1, JUMLAH_PUTARAN + 1):
    lama, hop_orkestrasi = ukur_orkestrasi()
    orkestrasi.append(lama)
    lama, hop_berantai = ukur_berantai()
    berantai.append(lama)
    if nomor % PUTARAN_PER_LAPORAN == 0:
      laporkan_kemajuan(nomor, orkestrasi, berantai, mulai)
  print(f"Selesai dalam {time.perf_counter() - mulai:.0f} detik.\n")
  return orkestrasi, berantai, hop_orkestrasi, hop_berantai


def cetak_ringkasan(orkestrasi: list, berantai: list, hop_orkestrasi: int,
                    hop_berantai: int) -> None:
  """Mencetak sebaran latensi kedua versi beserta selisih hop-nya.

  Sebarannya dilaporkan sebagai median, persentil ke-95, dan nilai terbesar,
  sebab gejala antrean hanya tampak pada nilai terbesar. Tidak mengembalikan
  nilai.
  """
  median_orkestrasi = statistics.median(orkestrasi)
  median_berantai = statistics.median(berantai)
  selisih = median_orkestrasi - median_berantai
  range_berantai = max(berantai) - min(berantai)
  lipat = range_berantai / selisih if selisih else 0.0
  menang = sum(1 for a, b in zip(orkestrasi, berantai) if b < a)
  tambahan = hop_orkestrasi - hop_berantai

  print(f"Putaran                      : {JUMLAH_PUTARAN}")
  print(f"Median orkestrasi            : {median_orkestrasi:.3f} ms")
  print(f"Median berantai              : {median_berantai:.3f} ms")
  print(f"Selisih median               : {selisih:.3f} ms")
  print(f"Orkestrasi lebih lambat      : "
        f"{median_orkestrasi / median_berantai:.2f} kali")
  print(f"Persentil ke-95 orkestrasi   : "
        f"{persentil(orkestrasi, 0.95):.3f} ms")
  print(f"Persentil ke-95 berantai     : {persentil(berantai, 0.95):.3f} ms")
  print(f"Terbesar orkestrasi          : {max(orkestrasi):.3f} ms")
  print(f"Terbesar berantai            : {max(berantai):.3f} ms")
  print(f"Range dalam versi berantai   : {range_berantai:.3f} ms")
  print(f"Range dibagi selisih         : {lipat:.1f} kali")
  print(f"Hop orkestrasi               : {hop_orkestrasi} per workflow")
  print(f"Hop berantai                 : {hop_berantai} per workflow")
  print(f"Tambahan hop                 : {tambahan} "
        f"({tambahan / hop_berantai * 100:.1f} persen)")
  print(f"Putaran berantai lebih cepat : {menang} dari {JUMLAH_PUTARAN}")


if __name__ == "__main__":
  kumpulan = server.KumpulanLayanan()
  kumpulan.nyalakan_semua()
  try:
    data.setel_ulang()
    panaskan()
    hasil = jalankan_putaran()
    cetak_ringkasan(*hasil)
  finally:
    kumpulan.matikan_semua()
  # Keluarannya: Tambahan hop                 : 1 (16.7 persen)
