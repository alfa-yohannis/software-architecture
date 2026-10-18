"""Ketiga pemroses yang menangani satu permintaan konversi kurs.

Pencatat menyimpan permintaan ke riwayat, pemeriksa menghitung nilai rupiahnya
lalu menandai yang melewati batas, dan pemberitahu menyusun teks bagi pemohon.
Ketiganya dipakai apa adanya oleh susunan sinkron, broker, maupun mediator,
sehingga pekerjaan yang diukur benar-benar sama pada ketiganya.

Dua pemroses tambahan di bagian bawah berkas hanya dipakai pada uji ketahanan.
PemeriksaGagal menirukan pemroses yang rusak berkala, sedangkan PemeriksaLambat
menirukan pemroses yang menunggu layanan luar.

Cara menjalankan: python pemroses.py
"""

import threading
import time

import domain

# PemeriksaGagal menolak setiap permintaan yang nomornya kelipatan angka ini.
# Kegagalan berkala dipilih agar terlihat berapa permintaan yang tetap selesai,
# bukan sekadar bahwa semuanya berhenti.
PERIODE_GAGAL = 5

# Jeda yang ditahan PemeriksaLambat pada setiap permintaan, dalam detik.
JEDA_LAMBAT = 0.005


class Pencatat:
  """Penyimpan riwayat permintaan, yaitu langkah pertama pada ketiga susunan.

  Riwayatnya disimpan di dalam memori agar bab ini tidak bergantung pada basis
  data. Penambahannya dijaga Lock, sebab pada susunan broker dan mediator
  pemroses ini berjalan di thread tersendiri.
  """

  nama = "pencatat"

  def __init__(self) -> None:
    """Menyiapkan riwayat kosong beserta kunci yang menjaga penambahannya."""
    self.riwayat = []
    self.kunci = threading.Lock()

  def tangani(self, permintaan: domain.Permintaan) -> str:
    """Menyusun satu baris riwayat, menyimpannya, lalu menandai langkahnya.

    Mengembalikan str berisi baris riwayat yang baru saja disimpan, sehingga
    pemanggil dapat menampilkannya tanpa membuka daftar riwayatnya.
    """
    baris = (f"{permintaan.nomor};{permintaan.kode_asal};"
             f"{permintaan.kode_tujuan};{permintaan.nominal:.2f}")
    with self.kunci:
      self.riwayat.append(baris)
    permintaan.catat_langkah(self.nama)
    return baris


class Pemeriksa:
  """Penghitung nilai rupiah sekaligus penanda permintaan yang perlu ditinjau.

  Pemroses inilah yang memuat tuntutan bisnis bab ini, yaitu permintaan besar
  tidak boleh lewat tanpa tinjauan. Tuntutan itu sengaja dibuat nyata, sebab
  pemroses yang hanya meneruskan panggilan tidak membuktikan apa pun.
  """

  nama = "pemeriksa"

  def __init__(self) -> None:
    """Menyiapkan pencacah permintaan yang ditandai beserta kuncinya."""
    self.jumlah_ditandai = 0
    self.kunci = threading.Lock()

  def tangani(self, permintaan: domain.Permintaan) -> float:
    """Menghitung nilai rupiah, menandai yang melewati batas, lalu mencatatnya.

    Mengembalikan float berisi nilai rupiah permintaan itu. Nilainya juga
    disimpan pada permintaannya, sebab pemberitahu membutuhkannya.
    """
    nilai = domain.hitung_konversi(permintaan.kode_asal,
                                   permintaan.kode_tujuan, permintaan.nominal)
    permintaan.nilai_rupiah = nilai
    permintaan.perlu_tinjauan = nilai >= domain.BATAS_TINJAUAN
    if permintaan.perlu_tinjauan:
      with self.kunci:
        self.jumlah_ditandai += 1
    permintaan.catat_langkah(self.nama)
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

  def tangani(self, permintaan: domain.Permintaan) -> str:
    """Menyusun teks pemberitahuan sesuai keputusan pemeriksa, lalu mencatatnya.

    Mengembalikan str berisi teks pemberitahuan. Teksnya juga disimpan pada
    permintaannya agar skrip pengujian dapat memeriksanya.
    """
    keadaan = "menunggu tinjauan" if permintaan.perlu_tinjauan else "disetujui"
    teks = (f"Permintaan {permintaan.nomor} senilai "
            f"Rp{permintaan.nilai_rupiah:,.0f} {keadaan}")
    permintaan.pemberitahuan = teks
    with self.kunci:
      self.jumlah_terkirim += 1
    permintaan.catat_langkah(self.nama)
    return teks


class PemeriksaGagal(Pemeriksa):
  """Pemeriksa yang menolak setiap permintaan kelipatan PERIODE_GAGAL.

  Dipakai pada uji ketahanan untuk menirukan pemroses yang rusak berkala,
  misalnya karena layanan kurs di belakangnya kadang menolak. Kegagalannya
  dilempar sebagai galat biasa, sehingga setiap susunan bebas menanganinya
  dengan caranya sendiri.
  """

  def tangani(self, permintaan: domain.Permintaan) -> float:
    """Melempar galat pada permintaan kelipatan tertentu, selebihnya normal.

    Mengembalikan float berisi nilai rupiah bagi permintaan yang lolos, dan
    melempar RuntimeError bagi permintaan yang kena giliran gagal.
    """
    if permintaan.nomor % PERIODE_GAGAL == 0:
      raise RuntimeError(f"Pemeriksaan permintaan {permintaan.nomor} gagal")
    return super().tangani(permintaan)


class PemeriksaLambat(Pemeriksa):
  """Pemeriksa yang menahan setiap permintaan selama JEDA_LAMBAT detik.

  Dipakai pada uji ketahanan untuk menirukan pemroses yang menunggu layanan
  luar. Jedanya kecil tetapi tetap ratusan kali lebih besar daripada
  pekerjaannya sendiri, sehingga penumpukan antreannya terlihat jelas.
  """

  def tangani(self, permintaan: domain.Permintaan) -> float:
    """Menunggu selama jeda tetap lebih dahulu, lalu bekerja seperti biasa.

    Mengembalikan float berisi nilai rupiah permintaan itu, sama seperti
    pemeriksa biasa.
    """
    time.sleep(JEDA_LAMBAT)
    return super().tangani(permintaan)


if __name__ == "__main__":
  contoh = domain.buat_permintaan(31, 3)
  Pencatat().tangani(contoh)
  Pemeriksa().tangani(contoh)
  print(Pemberitahu().tangani(contoh))
  # Keluarannya: Permintaan 31 senilai Rp520,000,000 menunggu tinjauan
  print(f"Langkah tercatat: {contoh.jejak}")
  # Keluarannya: Langkah tercatat: ['pencatat', 'pemeriksa', 'pemberitahu']
