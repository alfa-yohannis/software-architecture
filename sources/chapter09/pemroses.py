"""Ketiga pemroses yang menangani satu request konversi kurs.

Pencatat menyimpan request ke riwayat, pemeriksa menghitung nilai rupiahnya
lalu menandai yang melewati batas, dan pemberitahu menyusun teks bagi pemohon.
Ketiganya dipakai apa adanya oleh susunan sinkron, broker, maupun mediator,
sehingga pekerjaan yang diukur benar-benar sama pada ketiganya.

Dua pemroses tambahan di bagian bawah file hanya dipakai pada uji ketahanan.
PemeriksaGagal menirukan pemroses yang rusak berkala, sedangkan PemeriksaLambat
menirukan pemroses yang menunggu layanan luar.

Cara menjalankan: python pemroses.py
"""

import threading
import time

import domain

# PemeriksaGagal menolak setiap request yang nomornya kelipatan angka ini.
# Kegagalan berkala dipilih agar terlihat berapa request yang tetap selesai,
# bukan sekadar bahwa semuanya berhenti.
PERIODE_GAGAL = 5

# Jeda yang ditahan PemeriksaLambat pada setiap request, dalam detik.
JEDA_LAMBAT = 0.005


class Pencatat:
  """Penyimpan riwayat request, yaitu langkah pertama pada ketiga susunan.

  Riwayatnya disimpan di dalam memori agar bab ini tidak bergantung pada basis
  data. Penambahannya dijaga Lock, sebab pada susunan broker dan mediator
  pemroses ini berjalan di thread tersendiri.
  """

  nama = "pencatat"

  def __init__(self) -> None:
    """Menyiapkan riwayat kosong beserta kunci yang menjaga penambahannya."""
    self.riwayat = []
    self.kunci = threading.Lock()

  def tangani(self, request: domain.Request) -> str:
    """Menyusun satu baris riwayat, menyimpannya, lalu menandai langkahnya.

    Mengembalikan str berisi baris riwayat yang baru saja disimpan, sehingga
    pemanggil dapat menampilkannya tanpa membuka daftar riwayatnya.
    """
    baris = (f"{request.nomor};{request.kode_asal};"
             f"{request.kode_tujuan};{request.nominal:.2f}")
    with self.kunci:
      self.riwayat.append(baris)
    request.catat_langkah(self.nama)
    return baris


class Pemeriksa:
  """Penghitung nilai rupiah sekaligus penanda request yang perlu ditinjau.

  Pemroses inilah yang memuat tuntutan bisnis bab ini, yaitu request besar
  tidak boleh lewat tanpa tinjauan. Tuntutan itu sengaja dibuat nyata, sebab
  pemroses yang hanya meneruskan panggilan tidak membuktikan apa pun.
  """

  nama = "pemeriksa"

  def __init__(self) -> None:
    """Menyiapkan pencacah request yang ditandai beserta kuncinya."""
    self.jumlah_ditandai = 0
    self.kunci = threading.Lock()

  def tangani(self, request: domain.Request) -> float:
    """Menghitung nilai rupiah, menandai yang melewati batas, lalu mencatatnya.

    Mengembalikan float berisi nilai rupiah request itu. Nilainya juga
    disimpan pada request-nya, sebab pemberitahu membutuhkannya.
    """
    nilai = domain.hitung_konversi(request.kode_asal,
                                   request.kode_tujuan, request.nominal)
    request.nilai_rupiah = nilai
    request.perlu_tinjauan = nilai >= domain.BATAS_TINJAUAN
    if request.perlu_tinjauan:
      with self.kunci:
        self.jumlah_ditandai += 1
    request.catat_langkah(self.nama)
    return nilai


class Pemberitahu:
  """Penyusun teks pemberitahuan, yaitu langkah terakhir pada ketiga susunan.

  Isinya bergantung pada keputusan pemeriksa, sehingga pemroses ini hanya masuk
  akal dijalankan sesudah pemeriksaan. Urutan itulah yang menjadi bahan
  perbandingan antara topologi broker dan topologi mediator.
  """

  nama = "pemberitahu"

  def __init__(self) -> None:
    """Menyiapkan pencacah pemberitahuan yang sudah tersusun."""
    self.jumlah_terkirim = 0
    self.kunci = threading.Lock()

  def tangani(self, request: domain.Request) -> str:
    """Menyusun teks pemberitahuan sesuai keputusan pemeriksa, lalu mencatatnya.

    Mengembalikan str berisi teks pemberitahuan. Teksnya juga disimpan pada
    request-nya agar skrip pengujian dapat memeriksanya.
    """
    keadaan = "menunggu tinjauan" if request.perlu_tinjauan else "disetujui"
    teks = (f"Request {request.nomor} senilai "
            f"Rp{request.nilai_rupiah:,.0f} {keadaan}")
    request.pemberitahuan = teks
    with self.kunci:
      self.jumlah_terkirim += 1
    request.catat_langkah(self.nama)
    return teks


class PemeriksaGagal(Pemeriksa):
  """Pemeriksa yang menolak setiap request kelipatan PERIODE_GAGAL.

  Dipakai pada uji ketahanan untuk menirukan pemroses yang rusak berkala,
  misalnya karena layanan kurs di belakangnya kadang menolak. Kegagalannya
  dilempar sebagai error biasa, sehingga setiap susunan bebas menanganinya
  dengan caranya sendiri.
  """

  def tangani(self, request: domain.Request) -> float:
    """Melempar error pada request kelipatan tertentu, selebihnya normal.

    Mengembalikan float berisi nilai rupiah bagi request yang lolos, dan
    melempar RuntimeError bagi request yang kena giliran gagal.
    """
    if request.nomor % PERIODE_GAGAL == 0:
      raise RuntimeError(f"Pemeriksaan request {request.nomor} gagal")
    return super().tangani(request)


class PemeriksaLambat(Pemeriksa):
  """Pemeriksa yang menahan setiap request selama JEDA_LAMBAT detik.

  Dipakai pada uji ketahanan untuk menirukan pemroses yang menunggu layanan
  luar. Jedanya kecil tetapi tetap ratusan kali lebih besar daripada
  pekerjaannya sendiri, sehingga penumpukan antreannya terlihat jelas.
  """

  def tangani(self, request: domain.Request) -> float:
    """Menunggu selama jeda tetap lebih dahulu, lalu bekerja seperti biasa.

    Mengembalikan float berisi nilai rupiah request itu, sama seperti
    pemeriksa biasa.
    """
    time.sleep(JEDA_LAMBAT)
    return super().tangani(request)


if __name__ == "__main__":
  contoh = domain.buat_request(31, 3)
  Pencatat().tangani(contoh)
  Pemeriksa().tangani(contoh)
  print(Pemberitahu().tangani(contoh))
  # Keluarannya: Request 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Langkah tercatat: {contoh.jejak}")
  # Keluarannya: Langkah tercatat: ['pencatat', 'pemeriksa', 'pemberitahu']
