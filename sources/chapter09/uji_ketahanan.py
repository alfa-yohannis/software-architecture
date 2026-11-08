"""Menguji nasib ketiga susunan ketika satu pemroses gagal, lalu ketika lambat.

Skenario pertama memasang FailingValidator, yang menolak setiap request
kelipatan lima. Yang dihitung adalah berapa request tetap tuntas, berapa
yang sempat tercatat, dan siapa yang tahu langkah mana yang putus.

Skenario kedua memasang SlowValidator, yang menahan setiap request selama
lima milidetik. Yang dihitung adalah berapa lama publisher mengalami
blocking dan berapa event menumpuk di antrean. Susunan sinkron tidak punya
antrean, sehingga tekanannya muncul sebagai waktu tunggu publisher.

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
# Lebar tabel skenario dua yang dicetak berbaring, beserta urutan barisnya.
LEBAR_LABEL = 18
LEBAR_KOLOM = 10
BARIS_LAMBAT = (
  ("Publisher blocking", "blocking", ".1f"),
  ("Peak backlog", "puncak_backlog", "d"),
  ("Seluruh tercatat", "tercatat", ".1f"),
  ("Seluruh tuntas", "seluruh", ".1f"),
  ("Request tuntas", "tuntas", "d"),
)

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
    if susunan.antrean_backlog() == 0:
      time.sleep(JEDA_REDA)
      if susunan.antrean_backlog() == 0:
        return True
    time.sleep(JEDA_PANTAU)
  return False


def tunggu_tercatat(susunan, batas_detik: float) -> float:
  """Menunggu sampai seluruh request tercatat oleh recorder.

  Langkah pertama inilah yang dapat berjalan lepas dari langkah lambat di
  belakangnya, dan hanya topologi broker yang membiarkannya demikian.
  Mengembalikan float berisi waktu saat pencatatan terakhir teramati, dalam
  satuan perf_counter.
  """
  recorder = susunan.pemroses_bernama("recorder")
  batas_akhir = time.perf_counter() + batas_detik
  while (len(recorder.riwayat) < JUMLAH_PERMINTAAN
         and time.perf_counter() < batas_akhir):
    time.sleep(JEDA_PANTAU)
  return time.perf_counter()


def hitung_tuntas(daftar: list) -> int:
  """Mengembalikan int jumlah request yang seluruh langkahnya sudah lewat."""
  return sum(1 for request in daftar if request.selesai.is_set())


def jalankan_gagal(nama: str, perakit) -> dict:
  """Mengirim seluruh request pada susunan yang validator-nya rusak berkala.

  Mengembalikan dict berisi nama susunan, jumlah request yang tuntas, yang
  sempat tercatat, yang sempat diberitahukan, jumlah error tercatat, nomor
  request tempat pengiriman berhenti, dan satu contoh catatan error-nya.
  """
  susunan = perakit(pemroses.FailingValidator())
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
    "tercatat": len(susunan.pemroses_bernama("recorder").riwayat),
    "diberitahukan": susunan.pemroses_bernama("notifier").jumlah_terkirim,
    "galat": susunan.galat_tercatat(),
    "berhenti": berhenti_pada,
    "contoh": susunan.contoh_galat(),
  }
  susunan.tutup()
  return hasil


def jalankan_lambat(nama: str, perakit) -> dict:
  """Mengirim seluruh request pada susunan yang validator-nya lambat.

  Mengembalikan dict berisi nama susunan, lama publisher mengalami blocking,
  peak backlog yang sempat teramati, lama seluruh request tercatat, lama
  seluruh request tuntas, dan jumlah request yang tuntas.
  """
  susunan = perakit(pemroses.SlowValidator())
  daftar = buat_daftar(susunan)
  puncak_backlog = 0
  waktu_kirim = 0.0
  mulai = time.perf_counter()
  for request in daftar:
    awal = time.perf_counter()
    susunan.kirim(request)
    waktu_kirim += time.perf_counter() - awal
    puncak_backlog = max(puncak_backlog, susunan.antrean_backlog())
  tercatat = (tunggu_tercatat(susunan, BATAS_TUNGGU) - mulai) * MILIDETIK
  for request in daftar:
    request.tunggu(BATAS_TUNGGU)
  hasil = {
    "nama": nama,
    "blocking": waktu_kirim * MILIDETIK,
    "puncak_backlog": puncak_backlog,
    "tercatat": tercatat,
    "seluruh": (time.perf_counter() - mulai) * MILIDETIK,
    "tuntas": hitung_tuntas(daftar),
  }
  susunan.tutup()
  return hasil


def cetak_gagal(hasil: list) -> None:
  """Mencetak tabel skenario validator gagal beserta contoh catatan error-nya."""
  print(f"Skenario satu: validator menolak setiap request kelipatan "
        f"{pemroses.PERIODE_GAGAL}, dari {JUMLAH_PERMINTAAN} request.\n")
  print(f"{'Susunan':<10}{'Tuntas':>8}{'Tercatat':>10}{'Diberitahu':>12}"
        f"{'Error':>8}{'Berhenti':>10}")
  for baris in hasil:
    berhenti = baris["berhenti"] if baris["berhenti"] else "tidak"
    print(f"{baris['nama']:<10}{baris['tuntas']:>8d}{baris['tercatat']:>10d}"
          f"{baris['diberitahukan']:>12d}{baris['galat']:>8d}"
          f"{str(berhenti):>10}")
  print()
  for baris in hasil:
    print(f"Contoh catatan {baris['nama']:<9}: {baris['contoh']}")


def cetak_lambat(hasil: list) -> None:
  """Mencetak tabel skenario validator lambat, satu baris untuk setiap ukuran.

  Tabelnya dicetak berbaring, yaitu satu kolom per susunan, sebab kelima
  ukurannya berjudul panjang. Bentuk berbaring itu tetap muat pada jendela
  terminal yang sempit dan pada listing modul tanpa terpotong.
  """
  print(f"\nSkenario dua: validator menahan setiap request "
        f"{pemroses.JEDA_LAMBAT * MILIDETIK:.0f} ms.")
  print("Waktu dalam milidetik untuk seluruh request, bukan per "
        "request.\n")
  kepala = [f"{baris['nama']:>{LEBAR_KOLOM}}" for baris in hasil]
  print(f"{'Yang diukur':<{LEBAR_LABEL}}{''.join(kepala)}")
  for label, kunci, pola in BARIS_LAMBAT:
    sel = [f"{baris[kunci]:>{LEBAR_KOLOM}{pola}}" for baris in hasil]
    print(f"{label:<{LEBAR_LABEL}}{''.join(sel)}")


if __name__ == "__main__":
  print(f"Menjalankan dua skenario pada {len(SUSUNAN)} susunan.\n")
  hasil_gagal = [jalankan_gagal(nama, perakit) for nama, perakit in SUSUNAN]
  cetak_gagal(hasil_gagal)
  # Keluarannya, baris sinkron pada tabel skenario satu:
  # sinkron          4         5           4       0         5
  hasil_lambat = [jalankan_lambat(nama, perakit) for nama, perakit in SUSUNAN]
  cetak_lambat(hasil_lambat)
  # Keluarannya, baris peak backlog pada tabel skenario dua:
  # Peak backlog               0       100       100
