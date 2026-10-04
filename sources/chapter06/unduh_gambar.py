"""Mengunduh gambar contoh yang diolah pipa pada bab ini.

Gambar diambil dari layanan Lorem Picsum, yang melayani berkas JPEG berdasarkan
benih tetap. Benih yang tetap membuat kumpulan gambarnya sama pada setiap mesin,
sehingga angka pada latihan dapat dibandingkan antar mahasiswa.

Berkas hasil unduhan tidak ikut dilacak Git, sebab isinya bukan milik modul ini.
Bila jaringan tidak tersedia, pakai buat_gambar.py yang menghasilkan gambar
sintetis dengan ukuran serupa.

Cara menjalankan: python unduh_gambar.py
"""

import pathlib
import urllib.request

DIREKTORI_MASUKAN = pathlib.Path(__file__).parent / "masukan"
ALAMAT_POLA = "https://picsum.photos/seed/{benih}/1600/1200.jpg"
JUMLAH_GAMBAR = 60
AWALAN_BENIH = "apl"
BATAS_WAKTU = 30


def unduh_satu(nomor: int) -> bool:
  """Mengunduh satu gambar bila berkasnya belum ada di direktori masukan.

  Berkas yang sudah ada dilewati, sehingga skrip aman dijalankan berulang dan
  tidak membebani layanan sumbernya. Mengembalikan bool bernilai True bila
  unduhan benar-benar dilakukan.
  """
  tujuan = DIREKTORI_MASUKAN / f"contoh_{nomor:03d}.jpg"
  if tujuan.exists():
    return False
  alamat = ALAMAT_POLA.format(benih=f"{AWALAN_BENIH}{nomor}")
  with urllib.request.urlopen(alamat, timeout=BATAS_WAKTU) as jawaban:
    tujuan.write_bytes(jawaban.read())
  return True


def unduh_semua() -> tuple[int, int]:
  """Mengunduh seluruh gambar contoh, lalu melaporkan hasilnya.

  Kegagalan satu unduhan tidak menghentikan sisanya, sebab jaringan kampus
  kerap memutus sambungan di tengah jalan. Mengembalikan tuple berisi jumlah
  berkas baru dan jumlah berkas yang gagal.
  """
  DIREKTORI_MASUKAN.mkdir(exist_ok=True)
  baru, gagal = 0, 0
  for nomor in range(1, JUMLAH_GAMBAR + 1):
    try:
      if unduh_satu(nomor):
        baru += 1
    except Exception:
      gagal += 1
  return baru, gagal


if __name__ == "__main__":
  jumlah_baru, jumlah_gagal = unduh_semua()
  tersedia = len(list(DIREKTORI_MASUKAN.glob("*.jpg")))
  print(f"Gambar baru diunduh : {jumlah_baru}")
  # Keluarannya: Gambar baru diunduh : 60
  print(f"Unduhan gagal       : {jumlah_gagal}")
  print(f"Tersedia di masukan : {tersedia} berkas")
