"""Membandingkan besar berkas keadaan dengan besar event log.

Sepuluh ribu perintah yang sama dijalankan pada ketiga versi, lalu ukuran
berkas basis datanya dibaca. Versi CRUD dan versi CQRS menimpa baris yang sama
terus-menerus, sehingga berkasnya nyaris tidak tumbuh. Versi event sourcing
menambah satu baris untuk setiap perintah yang diterima, sehingga berkasnya
tumbuh sejalan dengan riwayatnya.

Versi event sourcing memasang snapshot setiap lima ratus perintah di sini,
sebab tanpa itu setiap perintah harus melipat seluruh log lebih dahulu.

Cara menjalankan: python ukur_penyimpanan.py
"""

import domain
import versi_cqrs
import versi_crud
import versi_event

JUMLAH_PERINTAH = 10_000
SNAPSHOT_TIAP = 500
LEBAR_LABEL = 36
BITA_PER_KIB = 1024


def jalankan_semua(buku, daftar: list[domain.Perintah],
                   snapshot_tiap: int = 0) -> int:
  """Menjalankan seluruh perintah pada satu versi lalu mencacah yang diterima.

  Argumen snapshot_tiap hanya dipakai versi event sourcing. Nilai nol berarti
  tidak ada snapshot yang dipasang. Mengembalikan int berisi jumlah perintah
  yang diterima, yaitu jumlah perubahan yang benar-benar tersimpan.
  """
  diterima = 0
  for nomor, perintah in enumerate(daftar, start=1):
    try:
      buku.jalankan(perintah)
      diterima += 1
    except domain.SaldoTidakCukup:
      continue
    if snapshot_tiap and nomor % snapshot_tiap == 0:
      buku.simpan_snapshot(perintah.pemilik)
  return diterima


def laporkan_versi(nama: str, ukuran: float, keterangan: str) -> None:
  """Mencetak satu baris laporan berisi ukuran berkas beserta isinya."""
  print(f"{'Ukuran berkas ' + nama:<{LEBAR_LABEL}}"
        f": {ukuran:8.1f} KiB  {keterangan}")


if __name__ == "__main__":
  perintah_uji = domain.bangkitkan_perintah(JUMLAH_PERINTAH)
  print(f"Menjalankan {JUMLAH_PERINTAH} perintah pada ketiga versi.",
        flush=True)
  print("Lamanya sekitar dua sampai tiga menit, sebab setiap perintah "
        "disimpan ke cakram.", flush=True)

  print("  versi CRUD", flush=True)
  buku_crud = versi_crud.BukuBesarCrud()
  buku_crud.siapkan()
  diterima_crud = jalankan_semua(buku_crud, perintah_uji)
  ukuran_crud = buku_crud.ukuran_kib()
  saldo_crud = buku_crud.baca_saldo(domain.PEMILIK_BAKU)
  buku_crud.tutup()

  print("  versi CQRS", flush=True)
  buku_cqrs = versi_cqrs.BukuBesarCqrs()
  buku_cqrs.siapkan()
  jalankan_semua(buku_cqrs, perintah_uji)
  ukuran_cqrs = buku_cqrs.ukuran_kib()
  saldo_cqrs = buku_cqrs.baca_saldo(domain.PEMILIK_BAKU)
  buku_cqrs.tutup()

  print("  versi event sourcing", flush=True)
  buku_event = versi_event.BukuBesarEvent()
  buku_event.siapkan()
  jalankan_semua(buku_event, perintah_uji, SNAPSHOT_TIAP)
  ukuran_event = buku_event.ukuran_kib()
  jumlah_event = buku_event.jumlah_event()
  saldo_event = buku_event.baca_saldo(domain.PEMILIK_BAKU)
  buku_event.tutup()

  saldo_sama = len({saldo_crud, saldo_cqrs, saldo_event}) == 1
  print(f"{'Perintah diterima':<{LEBAR_LABEL}}: {diterima_crud}")
  # Keluarannya: Perintah diterima                   : 9471
  print(f"{'Saldo akhir ketiga versi':<{LEBAR_LABEL}}"
        f": {saldo_crud} ({'sama' if saldo_sama else 'berbeda'})")
  # Keluarannya: Saldo akhir ketiga versi            : 858269000 (sama)
  print()
  laporkan_versi("keadaan CRUD", ukuran_crud, "1 baris keadaan")
  laporkan_versi("keadaan CQRS", ukuran_cqrs, "2 baris keadaan")
  laporkan_versi("event log", ukuran_event,
                 f"{jumlah_event} baris event")
  print()
  print(f"{'Log dibagi berkas keadaan CRUD':<{LEBAR_LABEL}}"
        f": {ukuran_event / ukuran_crud:.1f} kali")
  print(f"{'Bita per event':<{LEBAR_LABEL}}"
        f": {ukuran_event * BITA_PER_KIB / jumlah_event:.0f} bita")
  # Keluarannya: Bita per event                  : 69 bita
