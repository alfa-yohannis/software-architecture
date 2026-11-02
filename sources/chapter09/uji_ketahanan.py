"""Menguji nasib ketiga susunan ketika satu pemroses gagal, lalu ketika lambat.

Skenario pertama memasang PemeriksaGagal, yang menolak setiap request
kelipatan lima. Yang dihitung adalah berapa request tetap tuntas, berapa
yang sempat tercatat, dan siapa yang tahu langkah mana yang putus.

Skenario kedua memasang PemeriksaLambat, yang menahan setiap request selama
lima milidetik. Yang dihitung adalah berapa lama penerbit tertahan dan berapa
event menumpuk di antrean. Susunan sinkron tidak punya antrean, sehingga
tekanannya muncul sebagai waktu tunggu penerbit.

Cara menjalankan: python uji_ketahanan.py
"""

import time

import broker
import domain
import mediator
import pemroses
import sinkron

JUMLAH_PERMINTAAN = 100
BATAS_TUNGGU = 10.0
BATAS_REDA = 10.0
MILIDETIK = 1000.0
# Jeda penutup sesudah seluruh antrean terlihat kosong, dalam detik. Antrean
# dapat kosong sesaat padahal penangan terakhirnya masih bekerja.
JEDA_REDA = 0.05
JEDA_PANTAU = 0.001

SUSUNAN = (
  ("sinkron", sinkron.rakit),
  ("broker", broker.rakit),
  ("mediator", mediator.rakit),
)


def buat_daftar(susunan) -> list:
  """Mengembalikan list request contoh sebanyak JUMLAH_PERMINTAAN buah."""
  return [domain.buat_request(nomor, susunan.jumlah_langkah())
          for nomor in range(1, JUMLAH_PERMINTAAN + 1)]


def tunggu_reda(susunan, batas_detik: float) -> bool:
  """Menunggu sampai seluruh antrean kosong, lalu memberi jeda penutup.

  Dipakai pada skenario gagal, sebab sebagian request memang tidak akan
  pernah tuntas sehingga menunggu tanda selesainya akan sia-sia. Mengembalikan
  bool bernilai True bila antreannya benar-benar reda sebelum batas waktu.
  """
  batas_akhir = time.perf_counter() + batas_detik
  while time.perf_counter() < batas_akhir:
    if susunan.antrean_tertahan() == 0:
      time.sleep(JEDA_REDA)
      if susunan.antrean_tertahan() == 0:
        return True
    time.sleep(JEDA_PANTAU)
  return False


def tunggu_tercatat(susunan, batas_detik: float) -> float:
  """Menunggu sampai seluruh request tercatat oleh pencatat.

  Langkah pertama inilah yang dapat berjalan lepas dari langkah lambat di
  belakangnya, dan hanya topologi broker yang membiarkannya demikian.
  Mengembalikan float berisi waktu saat pencatatan terakhir teramati, dalam
  satuan perf_counter.
  """
  pencatat = susunan.pemroses_bernama("pencatat")
  batas_akhir = time.perf_counter() + batas_detik
  while (len(pencatat.riwayat) < JUMLAH_PERMINTAAN
         and time.perf_counter() < batas_akhir):
    time.sleep(JEDA_PANTAU)
  return time.perf_counter()


def hitung_tuntas(daftar: list) -> int:
  """Mengembalikan int jumlah request yang seluruh langkahnya sudah lewat."""
  return sum(1 for request in daftar if request.selesai.is_set())


def jalankan_gagal(nama: str, perakit) -> dict:
  """Mengirim seluruh request pada susunan yang pemeriksanya rusak berkala.

  Mengembalikan dict berisi nama susunan, jumlah request yang tuntas, yang
  sempat tercatat, yang sempat diberitahukan, jumlah galat tercatat, nomor
  request tempat pengiriman berhenti, dan satu contoh catatan galatnya.
  """
  susunan = perakit(pemroses.PemeriksaGagal())
  daftar = buat_daftar(susunan)
  berhenti_pada = None
  for request in daftar:
    try:
      susunan.kirim(request)
    except Exception:
      berhenti_pada = request.nomor
      break
  tunggu_reda(susunan, BATAS_REDA)
  hasil = {
    "nama": nama,
    "tuntas": hitung_tuntas(daftar),
    "tercatat": len(susunan.pemroses_bernama("pencatat").riwayat),
    "diberitahukan": susunan.pemroses_bernama("pemberitahu").jumlah_terkirim,
    "galat": susunan.galat_tercatat(),
    "berhenti": berhenti_pada,
    "contoh": susunan.contoh_galat(),
  }
  susunan.tutup()
  return hasil


def jalankan_lambat(nama: str, perakit) -> dict:
  """Mengirim seluruh request pada susunan yang pemeriksanya lambat.

  Mengembalikan dict berisi nama susunan, lama penerbit tertahan, kedalaman
  antrean terdalam yang sempat teramati, lama seluruh request tercatat, lama
  seluruh request tuntas, dan jumlah request yang tuntas.
  """
  susunan = perakit(pemroses.PemeriksaLambat())
  daftar = buat_daftar(susunan)
  terdalam = 0
  waktu_kirim = 0.0
  mulai = time.perf_counter()
  for request in daftar:
    awal = time.perf_counter()
    susunan.kirim(request)
    waktu_kirim += time.perf_counter() - awal
    terdalam = max(terdalam, susunan.antrean_tertahan())
  tercatat = (tunggu_tercatat(susunan, BATAS_TUNGGU) - mulai) * MILIDETIK
  for request in daftar:
    request.tunggu(BATAS_TUNGGU)
  hasil = {
    "nama": nama,
    "kembali": waktu_kirim * MILIDETIK,
    "terdalam": terdalam,
    "tercatat": tercatat,
    "seluruh": (time.perf_counter() - mulai) * MILIDETIK,
    "tuntas": hitung_tuntas(daftar),
  }
  susunan.tutup()
  return hasil


def cetak_gagal(hasil: list) -> None:
  """Mencetak tabel skenario pemeriksa gagal beserta contoh catatan galatnya."""
  print(f"Skenario satu: pemeriksa menolak setiap request kelipatan "
        f"{pemroses.PERIODE_GAGAL}, dari {JUMLAH_PERMINTAAN} request.\n")
  print(f"{'Susunan':<10}{'Tuntas':>8}{'Tercatat':>10}{'Diberitahu':>12}"
        f"{'Galat':>8}{'Berhenti':>10}")
  for baris in hasil:
    berhenti = baris["berhenti"] if baris["berhenti"] else "tidak"
    print(f"{baris['nama']:<10}{baris['tuntas']:>8d}{baris['tercatat']:>10d}"
          f"{baris['diberitahukan']:>12d}{baris['galat']:>8d}"
          f"{str(berhenti):>10}")
  print()
  for baris in hasil:
    print(f"Contoh catatan {baris['nama']:<9}: {baris['contoh']}")


def cetak_lambat(hasil: list) -> None:
  """Mencetak tabel skenario pemeriksa lambat beserta kedalaman antreannya."""
  print(f"\nSkenario dua: pemeriksa menahan setiap request "
        f"{pemroses.JEDA_LAMBAT * MILIDETIK:.0f} ms.")
  print("Waktu dalam milidetik untuk seluruh request, bukan per "
        "request.\n")
  print(f"{'Susunan':<10}{'Penerbit kembali':>18}{'Antrean terdalam':>18}"
        f"{'Seluruh tercatat':>18}{'Seluruh tuntas':>16}{'Tuntas':>8}")
  for baris in hasil:
    print(f"{baris['nama']:<10}{baris['kembali']:>18.1f}"
          f"{baris['terdalam']:>18d}{baris['tercatat']:>18.1f}"
          f"{baris['seluruh']:>16.1f}{baris['tuntas']:>8d}")


if __name__ == "__main__":
  print(f"Menjalankan dua skenario pada {len(SUSUNAN)} susunan.\n")
  hasil_gagal = [jalankan_gagal(nama, perakit) for nama, perakit in SUSUNAN]
  cetak_gagal(hasil_gagal)
  # Keluarannya baris sinkron: 4 tuntas, 5 tercatat, berhenti pada nomor 5
  hasil_lambat = [jalankan_lambat(nama, perakit) for nama, perakit in SUSUNAN]
  cetak_lambat(hasil_lambat)
  # Keluarannya baris broker: antrean terdalam 100 dari 100 request
