"""Mengukur data collision, yaitu dua unit mengubah baris yang sama sekaligus.

Selama replication lag belum lewat, dua unit dapat mengubah baris kelas yang
sama tanpa saling mengetahui. Ketika message replikasinya tiba, perubahan yang
satu menimpa perubahan yang lain, sehingga satu kuota terjual dua kali.

Richards dan Ford memberi rumus pegangan untuk menaksir seringnya kejadian itu,
yaitu N dikali UR kuadrat dibagi S, lalu dikali RL. N adalah jumlah unit yang
berbagi cache, UR laju perubahan per detik, S jumlah baris di dalam cache, dan
RL replication lag dalam detik. Skrip ini menjalankan keadaan yang sama lalu
membandingkan cacahan nyatanya dengan taksiran rumus itu.

Satu tabrakan dicacah setiap kali sebuah unit menerapkan message replikasi yang
versi sebelumnya tidak lagi cocok dengan versi baris di grid-nya. Cacahannya
karena itu tidak mungkin melebihi banyaknya message yang diterapkan, dan angka
itu ikut dicetak sebagai pembanding.

Cara menjalankan: python ukur_tabrakan.py
"""

import random
import statistics
import threading
import time

import domain
import grid as modul_grid

# Lama setiap putaran dijalankan, dalam detik.
LAMA_PUTARAN = 2.0
# Banyaknya putaran tiap keadaan, sebab satu kali jalan tidak cukup.
PUTARAN = 5
# Laju perubahan seluruh unit, dalam perubahan per detik.
LAJU_PERUBAHAN = 200
# Jumlah baris di dalam cache, yaitu banyaknya kelas yang diperebutkan.
JUMLAH_BARIS = 50
# Replication lag bawaan percobaan ini, dalam detik.
JEDA_BAKU = 0.100
# Jumlah unit bawaan percobaan ini.
UNIT_BAKU = 5
# Kuota besar agar kuotanya tidak habis sebelum putarannya selesai.
KUOTA_UKUR = 1000000
# Tambahan waktu tunggu sesudah putaran, agar message terakhir sempat diterapkan.
TAMBAHAN_TUNGGU = 0.05
# Lama menunggu thread unit selesai sesudah tanda berhenti dinyalakan.
BATAS_TUNGGU_UNIT = 1.0
# Nomor induk yang dipakai seluruh unit, sebab yang diukur hanya barisnya.
NIM_UJI = "202600000"
MILIDETIK = 1000.0

# Keadaan yang dicoba, masing-masing mengubah satu peubah saja.
KEADAAN = (
  ("acuan", UNIT_BAKU, JEDA_BAKU, JUMLAH_BARIS, LAJU_PERUBAHAN),
  ("lag 10 ms", UNIT_BAKU, 0.010, JUMLAH_BARIS, LAJU_PERUBAHAN),
  ("unit 2", 2, JEDA_BAKU, JUMLAH_BARIS, LAJU_PERUBAHAN),
  ("baris 10", UNIT_BAKU, JEDA_BAKU, 10, LAJU_PERUBAHAN),
  ("laju 400", UNIT_BAKU, JEDA_BAKU, JUMLAH_BARIS, 400),
)


def daftar_kelas_uji(jumlah_baris: int) -> list:
  """Menyusun nama kelas sebanyak baris yang diminta.

  Nama kelas dibuat sendiri agar jumlah barisnya dapat diatur, sebab jumlah
  baris itulah peubah S pada rumus taksiran. Mengembalikan list berisi kode
  kelas.
  """
  return [f"UJI{nomor:03d}" for nomor in range(jumlah_baris)]


def ubah_baris_acak(grid_unit: modul_grid.DataGrid, kelas_uji: list,
                    benih: int, jeda_antar_perubahan: float,
                    berhenti: threading.Event, pencacah: list,
                    kunci: threading.Lock) -> None:
  """Mengubah baris acak dengan laju tetap sampai tanda berhenti menyala.

  Pilihan barisnya diacak dengan benih tetap, sehingga putaran yang sama dapat
  diulang. Pencacah bersama dipakai agar laju nyata seluruh unit dapat dihitung
  sesudahnya. Tidak mengembalikan apa pun.
  """
  pengacak = random.Random(benih)
  nomor = 0
  while not berhenti.is_set():
    grid_unit.serap_replikasi()
    kode = pengacak.choice(kelas_uji)
    nomor += 1
    request = domain.Request(nomor, NIM_UJI, kode)
    grid_unit.kurangi(request)
    with kunci:
      pencacah[0] += 1
    time.sleep(jeda_antar_perubahan)


def jalankan_satu_putaran(jumlah_unit: int, jeda: float, jumlah_baris: int,
                          laju: int, putaran: int) -> dict:
  """Menjalankan satu putaran lalu mencacah tabrakan yang benar-benar terjadi.

  Setiap unit mengubah baris acak dengan laju yang dibagi rata, lalu menyerap
  replikasi dari unit lain. Benihnya digeser menurut nomor putaran, sehingga
  setiap putaran memilih baris yang berbeda. Mengembalikan dict berisi laju
  nyata, message yang diterapkan per detik, dan tabrakan per detik.
  """
  saluran = modul_grid.SaluranReplikasi(jeda, jumlah_unit)
  kelas_uji = daftar_kelas_uji(jumlah_baris)
  daftar_grid = []
  for nomor in range(1, jumlah_unit + 1):
    grid_unit = modul_grid.DataGrid(f"unit-{nomor}", saluran, KUOTA_UKUR,
                                    nomor)
    grid_unit.sisa = {kode: KUOTA_UKUR for kode in kelas_uji}
    grid_unit.versi = {kode: domain.VERSI_AWAL for kode in kelas_uji}
    daftar_grid.append(grid_unit)

  berhenti = threading.Event()
  jeda_antar_perubahan = jumlah_unit / laju
  pencacah = [0]
  kunci = threading.Lock()

  daftar_utas = []
  for nomor, grid_unit in enumerate(daftar_grid, start=1):
    benih = putaran * jumlah_unit + nomor
    utas = threading.Thread(target=ubah_baris_acak,
                            args=(grid_unit, kelas_uji, benih,
                                  jeda_antar_perubahan, berhenti, pencacah,
                                  kunci), daemon=True)
    utas.start()
    daftar_utas.append(utas)

  time.sleep(LAMA_PUTARAN)
  berhenti.set()
  for utas in daftar_utas:
    utas.join(timeout=BATAS_TUNGGU_UNIT)
  time.sleep(jeda + TAMBAHAN_TUNGGU)
  tabrakan = 0
  diterapkan = 0
  for grid_unit in daftar_grid:
    grid_unit.serap_replikasi()
    tabrakan += grid_unit.jumlah_tabrakan
    diterapkan += grid_unit.jumlah_terima
  saluran.tutup()
  return {
    "laju": pencacah[0] / LAMA_PUTARAN,
    "diterapkan_per_detik": diterapkan / LAMA_PUTARAN,
    "tabrakan_per_detik": tabrakan / LAMA_PUTARAN,
  }


def jalankan_satu_keadaan(nama: str, jumlah_unit: int, jeda: float,
                          jumlah_baris: int, laju: int) -> dict:
  """Mengulang satu keadaan sebanyak PUTARAN kali lalu meringkasnya.

  Taksiran rumus dihitung dari median laju nyata, bukan dari laju yang
  diminta, sebab tidur antar perubahan selalu sedikit lebih lama daripada yang
  diminta. Mengembalikan dict berisi median tiap angka, tabrakan terkecil dan
  terbesar antar putaran, serta taksiran rumusnya.
  """
  daftar_laju = []
  daftar_diterapkan = []
  daftar_tabrakan = []
  for putaran in range(PUTARAN):
    hasil = jalankan_satu_putaran(jumlah_unit, jeda, jumlah_baris, laju,
                                  putaran)
    daftar_laju.append(hasil["laju"])
    daftar_diterapkan.append(hasil["diterapkan_per_detik"])
    daftar_tabrakan.append(hasil["tabrakan_per_detik"])
  laju_nyata = statistics.median(daftar_laju)
  taksiran = jumlah_unit * (laju_nyata ** 2 / jumlah_baris) * jeda
  return {
    "nama": nama,
    "unit": jumlah_unit,
    "jeda": jeda,
    "baris": jumlah_baris,
    "laju": laju_nyata,
    "diterapkan": statistics.median(daftar_diterapkan),
    "tabrakan": statistics.median(daftar_tabrakan),
    "tabrakan_terkecil": min(daftar_tabrakan),
    "tabrakan_terbesar": max(daftar_tabrakan),
    "taksiran": taksiran,
  }


if __name__ == "__main__":
  print(f"Lama tiap putaran : {LAMA_PUTARAN:.1f} detik, {PUTARAN} putaran "
        f"tiap keadaan")
  print("Rumus taksiran    : N x (UR kuadrat / S) x RL")
  print("Kolom UR, diterapkan, tabrakan, dan taksiran dalam kejadian per "
        "detik\n")
  print(f"{'Keadaan':<10}{'N':>3}{'RL ms':>7}{'S':>5}{'UR':>8}"
        f"{'Diterapkan':>12}{'Tabrakan':>10}{'Taksiran':>10}")
  daftar_hasil = []
  for keadaan in KEADAAN:
    hasil_keadaan = jalankan_satu_keadaan(*keadaan)
    daftar_hasil.append(hasil_keadaan)
    print(f"{hasil_keadaan['nama']:<10}{hasil_keadaan['unit']:>3}"
          f"{hasil_keadaan['jeda'] * MILIDETIK:>7.0f}"
          f"{hasil_keadaan['baris']:>5}{hasil_keadaan['laju']:>8.1f}"
          f"{hasil_keadaan['diterapkan']:>12.1f}"
          f"{hasil_keadaan['tabrakan']:>10.1f}"
          f"{hasil_keadaan['taksiran']:>10.1f}")
  print("\nRagam tabrakan per detik antar putaran:")
  print(f"{'Keadaan':<10}{'Terkecil':>10}{'Median':>10}{'Terbesar':>10}")
  for hasil_keadaan in daftar_hasil:
    print(f"{hasil_keadaan['nama']:<10}"
          f"{hasil_keadaan['tabrakan_terkecil']:>10.1f}"
          f"{hasil_keadaan['tabrakan']:>10.1f}"
          f"{hasil_keadaan['tabrakan_terbesar']:>10.1f}")
  # Keluarannya, baris keadaan acuan pada tabel pertama:
  # acuan       5    100   50   200.0       800.0     222.0     400.0
