"""Menanyakan dua pertanyaan riwayat kepada ketiga versi penyimpanan.

Pertanyaan pertama menyangkut keadaan lampau, yaitu berapa saldo pada satu
waktu tertentu. Pertanyaan kedua menyangkut jumlah perubahan, yaitu berapa kali
saldo pernah berubah. Keduanya dijawab tanpa membuka kode versi mana pun, cukup
lewat metode yang sama.

Versi yang tidak mampu menjawab tetap mengembalikan objek Jawaban, sehingga
ketidakmampuannya tercetak sebagai hasil, bukan sebagai galat program. Jawaban
pembanding dihitung langsung dari daftar perintah, agar jawaban yang tercetak
dapat diperiksa kebenarannya.

Cara menjalankan: python tanya_riwayat.py
"""

import domain
import versi_cqrs
import versi_crud
import versi_event

JUMLAH_PERINTAH = 100
PERINTAH_PENANYA = 30
LEBAR_LABEL = 36
LEBAR_NAMA = 6


def isi_buku(buku, daftar: list[domain.Perintah]) -> None:
  """Menjalankan seluruh perintah pada satu versi sampai habis.

  Perintah yang ditolak aturan bisnis dilewati tanpa mengganggu perintah
  berikutnya, sama seperti pada skrip pengukuran lainnya.
  """
  buku.siapkan()
  for perintah in daftar:
    try:
      buku.jalankan(perintah)
    except domain.SaldoTidakCukup:
      continue


def hitung_pembanding(daftar: list[domain.Perintah],
                      batas_waktu: str) -> tuple[int, int]:
  """Menghitung kedua jawaban langsung dari daftar perintah di dalam memori.

  Hasilnya dipakai sebagai pembanding bagi jawaban ketiga versi, sehingga
  jawaban yang benar tidak ditentukan oleh versi mana pun. Mengembalikan tuple
  berisi saldo pada batas waktu beserta jumlah perubahan seluruhnya.
  """
  saldo = 0
  saldo_pada_batas = 0
  perubahan = 0
  for perintah in daftar:
    try:
      saldo = domain.periksa_perintah(saldo, perintah)
    except domain.SaldoTidakCukup:
      continue
    perubahan += 1
    if perintah.waktu <= batas_waktu:
      saldo_pada_batas = saldo
  return saldo_pada_batas, perubahan


def cetak_jawaban(nama: str, jawaban: domain.Jawaban) -> None:
  """Mencetak satu jawaban beserta alasannya dalam bentuk yang seragam.

  Versi yang menolak menjawab dicetak dengan kata tidak terjawab, sehingga
  lembar isian latihan dapat diisi dari baris ini apa adanya.
  """
  if jawaban.bisa:
    print(f"  {nama:<{LEBAR_NAMA}}: {jawaban.nilai} ({jawaban.alasan})")
  else:
    print(f"  {nama:<{LEBAR_NAMA}}: tidak terjawab ({jawaban.alasan})")


if __name__ == "__main__":
  perintah_uji = domain.bangkitkan_perintah(JUMLAH_PERINTAH)
  batas = domain.waktu_perintah_ke(PERINTAH_PENANYA)
  buku_crud = versi_crud.BukuBesarCrud()
  buku_cqrs = versi_cqrs.BukuBesarCqrs()
  buku_event = versi_event.BukuBesarEvent()
  daftar_versi = [("CRUD", buku_crud), ("CQRS", buku_cqrs),
                  ("event", buku_event)]
  for nama_versi, buku_versi in daftar_versi:
    isi_buku(buku_versi, perintah_uji)

  saldo_pembanding, perubahan_pembanding = hitung_pembanding(perintah_uji,
                                                             batas)
  print(f"Pertanyaan 1: berapa saldo pada {batas}")
  for nama_versi, buku_versi in daftar_versi:
    cetak_jawaban(nama_versi,
                  buku_versi.jawab_saldo_pada(domain.PEMILIK_BAKU, batas))
  print(f"  {'pembanding':<{LEBAR_NAMA}}: {saldo_pembanding}")
  # Keluarannya: pembanding: 2132000

  print("\nPertanyaan 2: berapa kali saldo berubah")
  for nama_versi, buku_versi in daftar_versi:
    cetak_jawaban(nama_versi,
                  buku_versi.jawab_jumlah_perubahan(domain.PEMILIK_BAKU))
  print(f"  {'pembanding':<{LEBAR_NAMA}}: {perubahan_pembanding}")
  # Keluarannya: pembanding: 95

  print()
  for nama_versi, buku_versi in daftar_versi:
    terjawab = sum([
      buku_versi.jawab_saldo_pada(domain.PEMILIK_BAKU, batas).bisa,
      buku_versi.jawab_jumlah_perubahan(domain.PEMILIK_BAKU).bisa,
    ])
    print(f"{'Pertanyaan terjawab ' + nama_versi:<{LEBAR_LABEL}}"
          f": {terjawab} dari 2")
    buku_versi.tutup()
  # Keluarannya: Pertanyaan terjawab event           : 2 dari 2
