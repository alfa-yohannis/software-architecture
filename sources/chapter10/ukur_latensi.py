"""Mengukur latensi tulis dan latensi baca pada ketiga versi penyimpanan.

Seratus perintah dijalankan lebih dahulu, lalu seratus kueri saldo dijalankan
di atas keadaan akhir yang sama. Setiap perintah dan setiap kueri diukur
sendiri-sendiri, sehingga yang dilaporkan adalah sebaran seratus angka, bukan
satu angka tunggal.

Versi event sourcing dijalankan tanpa snapshot di sini, sehingga setiap kueri
melipat seluruh event log. Akibat pemasangan snapshot diukur terpisah oleh
ukur_penghitungan_ulang.py.

Cara menjalankan: python ukur_latensi.py
"""

import time

import domain
import sebaran
import versi_cqrs
import versi_crud
import versi_event

JUMLAH_PERINTAH = 100
JUMLAH_KUERI = 100
MILIDETIK = 1000.0
# Lebar label laporan, disamakan agar angkanya berbaris rapi ke bawah.
LEBAR_LABEL = 36


def ukur_tulis(buku, daftar_perintah: list[domain.Perintah]) -> list[float]:
  """Menjalankan seluruh perintah sambil mengukur waktu satu per satu.

  Perintah yang ditolak aturan bisnis tetap diukur, sebab penolakan pun
  menuntut pembacaan keadaan lebih dahulu. Mengembalikan list berisi latensi
  setiap perintah dalam milidetik.
  """
  latensi = []
  for perintah in daftar_perintah:
    mulai = time.perf_counter()
    try:
      buku.jalankan(perintah)
    except domain.SaldoTidakCukup:
      pass
    latensi.append((time.perf_counter() - mulai) * MILIDETIK)
  return latensi


def ukur_baca(buku, jumlah: int = JUMLAH_KUERI) -> list[float]:
  """Menanyakan saldo sekarang berulang kali sambil mengukur waktunya.

  Pertanyaannya sengaja sama pada ketiga versi, yaitu berapa saldo sekarang,
  agar yang dibandingkan benar-benar cara penyimpanannya. Mengembalikan list
  berisi latensi setiap kueri dalam milidetik.
  """
  latensi = []
  for _ in range(jumlah):
    mulai = time.perf_counter()
    buku.baca_saldo(domain.PEMILIK_BAKU)
    latensi.append((time.perf_counter() - mulai) * MILIDETIK)
  return latensi


def jalankan_satu_versi(buku, daftar_perintah: list[domain.Perintah]) -> dict:
  """Mengukur satu versi dari tabel kosong sampai seratus kueri selesai.

  Mengembalikan dict berisi sebaran latensi tulis, sebaran latensi baca, dan
  saldo akhirnya. Saldo akhir ikut dikembalikan sebab ketiga versi wajib
  berakhir pada angka yang sama.
  """
  buku.siapkan()
  tulis = ukur_tulis(buku, daftar_perintah)
  baca = ukur_baca(buku)
  saldo = buku.baca_saldo(domain.PEMILIK_BAKU)
  buku.tutup()
  return {"tulis": tulis, "baca": baca, "saldo": saldo}


def bandingkan(jenis: str, nama_lambat: str, lambat: list[float],
               nama_cepat: str, cepat: list[float]) -> None:
  """Mencetak selisih median kedua versi beserta ragam pengukurannya.

  Selisih yang lebih kecil daripada rentang di dalam satu versi belum dapat
  disebut ada, sehingga kedua angka itu dicetak berdampingan. Pencacahan per
  putaran ditambahkan sebab pencacahan lebih peka daripada median. Pembagian
  memakai nilai mutlak selisihnya, sebab yang dibandingkan adalah besarnya,
  bukan arahnya.
  """
  sebaran_lambat = sebaran.Sebaran(lambat)
  sebaran_cepat = sebaran.Sebaran(cepat)
  selisih = sebaran_lambat.median() - sebaran_cepat.median()
  rentang = sebaran_cepat.rentang()
  menang = sum(1 for a, b in zip(lambat, cepat) if a > b)
  judul = f"Selisih median {jenis} {nama_lambat} dan {nama_cepat}"
  print(f"{judul:<{LEBAR_LABEL}}: {selisih:.4f} ms")
  print(f"{'Rentang di dalam ' + nama_cepat:<{LEBAR_LABEL}}: {rentang:.4f} ms")
  print(f"{'Rentang dibagi selisih':<{LEBAR_LABEL}}"
        f": {rentang / abs(selisih):.1f} kali")
  print(f"{jenis.capitalize() + ' ' + nama_lambat + ' lebih lambat':<{LEBAR_LABEL}}"
        f": {menang} dari {len(lambat)}")


if __name__ == "__main__":
  perintah_uji = domain.bangkitkan_perintah(JUMLAH_PERINTAH)
  print(f"Menjalankan {JUMLAH_PERINTAH} perintah lalu {JUMLAH_KUERI} kueri "
        f"pada ketiga versi.", flush=True)
  hasil = {
    "CRUD": jalankan_satu_versi(versi_crud.BukuBesarCrud(), perintah_uji),
    "CQRS": jalankan_satu_versi(versi_cqrs.BukuBesarCqrs(), perintah_uji),
    "event": jalankan_satu_versi(versi_event.BukuBesarEvent(), perintah_uji),
  }

  saldo_akhir = {isi["saldo"] for isi in hasil.values()}
  cocok = "sama" if len(saldo_akhir) == 1 else "berbeda"
  print(f"{'Saldo akhir ketiga versi':<{LEBAR_LABEL}}"
        f": {max(saldo_akhir)} ({cocok})")
  # Keluarannya: Saldo akhir ketiga versi            : 8425000 (sama)
  print()
  for nama_versi, isi_versi in hasil.items():
    print(sebaran.Sebaran(isi_versi["tulis"]).baris(
      f"Latensi tulis {nama_versi}", LEBAR_LABEL))
  print()
  for nama_versi, isi_versi in hasil.items():
    print(sebaran.Sebaran(isi_versi["baca"]).baris(
      f"Latensi baca {nama_versi}", LEBAR_LABEL))
  print()
  bandingkan("baca", "event", hasil["event"]["baca"],
             "CQRS", hasil["CQRS"]["baca"])
  print()
  bandingkan("baca", "CQRS", hasil["CQRS"]["baca"],
             "CRUD", hasil["CRUD"]["baca"])
  print()
  bandingkan("tulis", "CQRS", hasil["CQRS"]["tulis"],
             "CRUD", hasil["CRUD"]["tulis"])
  # Keluarannya: Tulis CQRS lebih lambat             : 99 dari 100
