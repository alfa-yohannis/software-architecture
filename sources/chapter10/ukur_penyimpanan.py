"""Membandingkan besar file keadaan dengan besar event log.

Sepuluh ribu command yang sama dijalankan pada ketiga versi, lalu ukuran
file basis datanya dibaca. Versi CRUD dan versi CQRS menimpa baris yang sama
terus-menerus, sehingga file-nya nyaris tidak tumbuh. Versi event sourcing
menambah satu baris untuk setiap command yang diterima, sehingga file-nya
tumbuh sejalan dengan riwayatnya.

Versi event sourcing memasang snapshot setiap lima ratus command di sini,
sebab tanpa itu setiap command harus melipat seluruh log lebih dahulu.

Cara menjalankan: python ukur_penyimpanan.py
"""

import domain
import versi_cqrs
import versi_crud
import versi_event

JUMLAH_COMMAND = 10_000
SNAPSHOT_TIAP = 500
LEBAR_LABEL = 36
BITA_PER_KIB = 1024


def jalankan_semua(buku, daftar: list[domain.Command],
                   snapshot_tiap: int = 0) -> int:
  """Menjalankan seluruh command pada satu versi lalu mencacah yang diterima.

  Argumen snapshot_tiap hanya dipakai versi event sourcing. Nilai nol berarti
  tidak ada snapshot yang dipasang. Mengembalikan int berisi jumlah command
  yang diterima, yaitu jumlah perubahan yang benar-benar tersimpan.
  """
  diterima = 0
  for nomor, command in enumerate(daftar, start=1):
    try:
      buku.jalankan(command)
      diterima += 1
    except domain.SaldoTidakCukup:
      continue
    if snapshot_tiap and nomor % snapshot_tiap == 0:
      buku.simpan_snapshot(command.pemilik)
  return diterima


def laporkan_versi(nama: str, ukuran: float, keterangan: str) -> None:
  """Mencetak satu baris laporan berisi ukuran file beserta isinya."""
  print(f"{'Ukuran file ' + nama:<{LEBAR_LABEL}}"
        f": {ukuran:8.1f} KiB  {keterangan}")


if __name__ == "__main__":
  command_uji = domain.bangkitkan_command(JUMLAH_COMMAND)
  print(f"Menjalankan {JUMLAH_COMMAND} command pada ketiga versi.",
        flush=True)
  print("Lamanya bergantung pada cakram, sebab setiap command disimpan "
        "dengan commit tersendiri.", flush=True)

  print("  versi CRUD", flush=True)
  buku_crud = versi_crud.BukuBesarCrud()
  buku_crud.siapkan()
  diterima_crud = jalankan_semua(buku_crud, command_uji)
  ukuran_crud = buku_crud.ukuran_kib()
  saldo_crud = buku_crud.baca_saldo(domain.PEMILIK_BAKU)
  buku_crud.tutup()

  print("  versi CQRS", flush=True)
  buku_cqrs = versi_cqrs.BukuBesarCqrs()
  buku_cqrs.siapkan()
  jalankan_semua(buku_cqrs, command_uji)
  ukuran_cqrs = buku_cqrs.ukuran_kib()
  saldo_cqrs = buku_cqrs.baca_saldo(domain.PEMILIK_BAKU)
  buku_cqrs.tutup()

  print("  versi event sourcing", flush=True)
  buku_event = versi_event.BukuBesarEvent()
  buku_event.siapkan()
  jalankan_semua(buku_event, command_uji, SNAPSHOT_TIAP)
  ukuran_event = buku_event.ukuran_kib()
  jumlah_event = buku_event.jumlah_event()
  saldo_event = buku_event.baca_saldo(domain.PEMILIK_BAKU)
  buku_event.tutup()

  saldo_sama = len({saldo_crud, saldo_cqrs, saldo_event}) == 1
  print(f"{'Command diterima':<{LEBAR_LABEL}}: {diterima_crud}")
  # Keluarannya: Command diterima                   : 9995
  print(f"{'Saldo akhir ketiga versi':<{LEBAR_LABEL}}"
        f": {saldo_crud} ({'sama' if saldo_sama else 'berbeda'})")
  # Keluarannya: Saldo akhir ketiga versi            : 1236954000 (sama)
  print()
  laporkan_versi("keadaan CRUD", ukuran_crud, "1 baris keadaan")
  laporkan_versi("keadaan CQRS", ukuran_cqrs, "2 baris keadaan")
  laporkan_versi("event log", ukuran_event,
                 f"{jumlah_event} baris event")
  print()
  print(f"{'Log dibagi file keadaan CRUD':<{LEBAR_LABEL}}"
        f": {ukuran_event / ukuran_crud:.1f} kali")
  print(f"{'Bita per event':<{LEBAR_LABEL}}"
        f": {ukuran_event * BITA_PER_KIB / jumlah_event:.0f} bita")
  # Keluarannya: Bita per event                      : 68 bita
