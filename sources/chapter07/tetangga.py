"""Susunan unstructured, yaitu setiap node hanya mengenal beberapa neighbor.

Kunci disebar acak, dan tidak ada satu node pun yang tahu di mana sebuah kunci
berada. Lookup karena itu disebarkan ke seluruh neighbor, lalu diteruskan
lagi oleh neighbor tersebut sampai batas hop tercapai. Cara ini dipakai
Gnutella, dan batas hop-nya lazim disebut Time To Live (TTL).

Dua aturan dipakai persis seperti pada Gnutella. Pertama, sebuah pertanyaan
tidak pernah dikembalikan kepada pengirimnya. Kedua, node yang sudah pernah
menerima pertanyaan yang sama membuangnya tanpa meneruskan. Tanpa aturan kedua,
pertanyaan akan berputar di dalam jaringan tanpa henti.

Penyebarannya tidak berhenti walaupun kuncinya sudah ditemukan, sebab tidak ada
satu node pun yang mengetahui bahwa lookup itu sudah selesai. Akibatnya
ongkos lookup hampir tidak bergantung pada letak kuncinya.

Cara menjalankan: python neighbor.py
"""

import collections

import domain
import jaringan

# Rata-rata neighbor per node. Angka tiga cukup untuk membuat jaringannya
# tersambung, tetapi masih cukup kecil untuk dibaca pada gambar.
TETANGGA_PER_SIMPUL = 3
# Batas hop sebuah pertanyaan, yaitu Time To Live pada Gnutella.
BATAS_LOMPATAN = 4


class FloodingNetwork(jaringan.Network):
  """Jaringan acak tanpa struktur, dengan lookup yang disebar bertahap."""

  nama = "unstructured"

  def susun(self) -> None:
    """Menyambung node secara acak lalu menyebar kunci ke sembarang node."""
    self.sambungkan_acak()
    self.sebarkan_kunci()

  def sambungkan_acak(self) -> None:
    """Membuat sambungan acak sampai rata-rata neighbor-nya tercapai.

    Putaran pertama menyambungkan setiap node baru ke salah satu node yang
    sudah ada, sehingga seluruh jaringan dijamin tersambung. Sisa sambungannya
    diambil acak, dan sambungan acak itulah yang membuat susunan ini tidak
    dapat ditebak.
    """
    for nomor in range(1, self.jumlah_simpul):
      self.sambungkan(nomor, self.acak.randrange(nomor))
    sasaran_sisi = self.jumlah_simpul * TETANGGA_PER_SIMPUL // 2
    while self.jumlah_sisi() < sasaran_sisi:
      nomor_a = self.acak.randrange(self.jumlah_simpul)
      nomor_b = self.acak.randrange(self.jumlah_simpul)
      self.sambungkan(nomor_a, nomor_b)

  def sebarkan_kunci(self) -> None:
    """Menitipkan setiap kunci kepada satu node yang dipilih acak.

    Letaknya tidak dicatat di mana pun, sehingga lookup tidak punya petunjuk
    apa pun selain menyusuri neighbor.
    """
    for kunci in domain.daftar_kunci():
      nomor = self.acak.randrange(self.jumlah_simpul)
      self.simpul[nomor].simpan(kunci, domain.nilai_kurs(kunci))

  def cari(self, nomor_peminta: int, kunci: str) -> jaringan.LookupResult:
    """Menyebarkan pertanyaan ke seluruh neighbor sampai batas hop.

    Mengembalikan LookupResult berisi jumlah pesan yang melintas, jumlah hop
    sampai pemegang kunci, dan nilai kursnya. Pesan jawaban dihitung sebanyak
    hop, sebab jawabannya pulang lewat jalur yang sama.
    """
    peminta = self.simpul[nomor_peminta]
    if not peminta.hidup:
      return jaringan.LookupResult(kunci, None, 0, 0)
    nilai = peminta.ambil(kunci)
    if nilai is not None:
      return jaringan.LookupResult(kunci, nilai, 0, 0)
    return self.sebarkan_pertanyaan(nomor_peminta, kunci)

  def sebarkan_pertanyaan(self, nomor_peminta: int, kunci: str):
    """Menelusuri jaringan selapis demi selapis mulai dari node peminta.

    Mengembalikan LookupResult satu lookup. Setiap perpindahan pesan di atas satu
    sambungan dihitung satu, termasuk pesan yang jatuh ke node mati dan pesan
    berulang yang dibuang penerimanya.
    """
    pesan = 0
    nilai = None
    lompatan = 0
    terlihat = {nomor_peminta}
    antrean = collections.deque([(nomor_peminta, -1, 0)])
    while antrean:
      nomor, pengirim, jarak = antrean.popleft()
      if jarak >= BATAS_LOMPATAN:
        continue
      for tujuan in self.simpul[nomor].tetangga:
        if tujuan == pengirim:
          continue
        pesan += 1
        if tujuan in terlihat or not self.simpul[tujuan].hidup:
          continue
        terlihat.add(tujuan)
        temuan = self.simpul[tujuan].ambil(kunci)
        if nilai is None and temuan is not None:
          nilai = temuan
          lompatan = jarak + 1
        antrean.append((tujuan, nomor, jarak + 1))
    return jaringan.LookupResult(kunci, nilai, pesan + lompatan, lompatan)


if __name__ == "__main__":
  jaringan_tetangga = FloodingNetwork(8)
  print(jaringan_tetangga.ringkas())
  for nomor_simpul in range(jaringan_tetangga.jumlah_simpul):
    simpul_ini = jaringan_tetangga.simpul[nomor_simpul]
    print(f"  node {nomor_simpul} neighbor {sorted(simpul_ini.tetangga)}"
          f" kunci {len(simpul_ini.simpanan)}")
  hasil = jaringan_tetangga.cari(3, "EUR/IDR")
  print(f"Lookup EUR/IDR dari node 3 : {hasil}")
  # Keluarannya: Lookup EUR/IDR dari node 3 : LookupResult(EUR/IDR,
  # nilai=20368.91, pesan=20, hop=3)
