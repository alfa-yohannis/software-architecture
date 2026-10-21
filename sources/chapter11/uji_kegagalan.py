"""Menghitung permintaan yang masih terlayani ketika satu bagian mati.

Tiga keadaan diuji berurutan. Keadaan pertama adalah keadaan sehat, sebagai
pembanding. Keadaan kedua mematikan satu bidang domain, yaitu kurs. Pada versi
service-based bidang itu berupa proses tersendiri, sehingga hanya proses itu
yang mati. Pada versi monolit bidang itu tidak punya proses sendiri, sehingga
mematikannya berarti mematikan seluruh aplikasi.

Keadaan ketiga menahan berkas basis data bersama dengan kunci penuh SQLite.
Keadaan itu menimpa kedua versi sekaligus, sebab keduanya membaca berkas yang
sama. Angka pada keadaan ketiga itulah pengingat bahwa pemecahan proses tidak
dengan sendirinya memecah titik kegagalan.

Cara menjalankan: python uji_kegagalan.py
"""

import sqlite3

import basis_data
import jalankan_layanan
import alamat

LAYANAN_DIMATIKAN = "kurs"
PERINTAH_KUNCI = "BEGIN EXCLUSIVE"
PERINTAH_LEPAS = "ROLLBACK"


def hitung_terlayani(porta: int) -> tuple[int, list[str]]:
  """Mencoba keempat jenis permintaan pada satu versi lalu mencacahnya.

  Permintaan dianggap terlayani hanya bila jawabannya berkode 200, sehingga
  jawaban 503 dari gerbang maupun sambungan yang ditolak sama-sama terhitung
  gagal. Mengembalikan tuple berisi int jumlah yang terlayani dan list nama
  permintaan yang berhasil.
  """
  berhasil = []
  for permintaan in jalankan_layanan.JENIS_PERMINTAAN:
    lolos, _ = jalankan_layanan.panggil(porta, permintaan)
    if lolos:
      berhasil.append(permintaan[0])
  return len(berhasil), berhasil


def kunci_basis_data() -> sqlite3.Connection:
  """Menahan berkas basis data bersama dengan kunci penuh SQLite.

  Mode jurnal bawaan dipakai justru agar pembacaan ikut tertahan. Pada mode
  WAL pembaca tidak akan terhalang, sehingga percobaan ini tidak akan
  memperlihatkan apa pun. Mengembalikan objek koneksi yang memegang kuncinya,
  dan koneksi itu wajib dilepaskan pemanggil.
  """
  koneksi = sqlite3.connect(basis_data.BERKAS,
                            timeout=basis_data.BATAS_TUNGGU_KUNCI,
                            isolation_level=None)
  koneksi.execute(PERINTAH_KUNCI)
  return koneksi


def lepas_kunci(koneksi: sqlite3.Connection) -> None:
  """Melepaskan kunci penuh yang sedang ditahan lalu menutup koneksinya.

  Dipanggil pada blok finally, sebab kunci yang tertinggal membuat latihan
  berikutnya gagal tanpa sebab yang jelas. Tidak mengembalikan apa pun.
  """
  koneksi.execute(PERINTAH_LEPAS)
  koneksi.close()


def cetak_baris(keadaan: str, monolit: int, layanan: int) -> None:
  """Mencetak satu baris ringkasan dengan lebar kolom yang tetap.

  Lebar kolomnya disamakan agar ketiga baris mudah dibaca berdampingan dan
  mudah disalin ke dalam tabel latihan. Tidak mengembalikan apa pun.
  """
  jumlah = len(jalankan_layanan.JENIS_PERMINTAAN)
  print(f"{keadaan:<30} {monolit} dari {jumlah}    {layanan} dari {jumlah}")


def cetak_rincian(judul: str, berhasil: list[str]) -> None:
  """Mencetak nama permintaan yang masih terlayani pada satu keadaan.

  Rincian ini yang menjawab pertanyaan latihan, yaitu permintaan mana yang
  selamat, bukan sekadar berapa banyak. Tidak mengembalikan apa pun.
  """
  isi = ", ".join(berhasil) if berhasil else "tidak ada"
  print(f"  {judul:<28} {isi}")


if __name__ == "__main__":
  basis_data.siapkan()
  semua_proses = {
    **jalankan_layanan.PROSES_MONOLIT,
    **jalankan_layanan.PROSES_LAYANAN,
  }
  proses_hidup = jalankan_layanan.nyalakan(semua_proses)
  try:
    sehat_monolit, rinci_monolit = hitung_terlayani(alamat.PORTA_MONOLIT)
    sehat_layanan, rinci_layanan = hitung_terlayani(alamat.PORTA_GERBANG)

    jalankan_layanan.matikan_satu(proses_hidup, "monolit")
    jalankan_layanan.matikan_satu(proses_hidup, LAYANAN_DIMATIKAN)
    mati_monolit, rinci_mati_monolit = hitung_terlayani(alamat.PORTA_MONOLIT)
    mati_layanan, rinci_mati_layanan = hitung_terlayani(alamat.PORTA_GERBANG)

    jalankan_layanan.matikan(proses_hidup)
    proses_hidup = jalankan_layanan.nyalakan(semua_proses)
    penahan = kunci_basis_data()
    try:
      kunci_monolit, _ = hitung_terlayani(alamat.PORTA_MONOLIT)
      kunci_layanan, _ = hitung_terlayani(alamat.PORTA_GERBANG)
    finally:
      lepas_kunci(penahan)

    print(f"{'Keadaan':<30} {'Monolit':<10} {'Service-based'}")
    cetak_baris("Seluruh proses hidup", sehat_monolit, sehat_layanan)
    # Keluarannya: Seluruh proses hidup           4 dari 4    4 dari 4
    cetak_baris("Bidang kurs dimatikan", mati_monolit, mati_layanan)
    # Keluarannya: Bidang kurs dimatikan          0 dari 4    2 dari 4
    cetak_baris("Basis data bersama dikunci", kunci_monolit, kunci_layanan)
    # Keluarannya: Basis data bersama dikunci     0 dari 4    0 dari 4
    print("Permintaan yang masih terlayani saat bidang kurs dimatikan")
    cetak_rincian("Monolit", rinci_mati_monolit)
    cetak_rincian("Service-based", rinci_mati_layanan)
  finally:
    jalankan_layanan.matikan(proses_hidup)
