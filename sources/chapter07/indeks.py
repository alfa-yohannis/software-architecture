"""Susunan client-server, yaitu satu node indeks yang mengetahui semuanya.

Seluruh kunci dititipkan kepada satu node saja. Node lain tidak menyimpan
apa pun, dan tidak saling mengenal, sehingga satu-satunya jalan menemukan kurs
adalah bertanya kepada indeks. Susunan inilah yang dipakai Napster pada mulanya,
yaitu daftar file disimpan terpusat sedangkan berkasnya sendiri berpindah
langsung antar pemakai.

Ongkosnya paling murah, yaitu dua pesan dan satu hop untuk kunci mana pun.
Harganya baru terlihat ketika node indeksnya mati.

Cara menjalankan: python indeks.py
"""

import domain
import jaringan

# Node nomor nol berperan sebagai indeks pada susunan ini. Nomor yang sama
# dipakai kedua susunan lain sebagai node biasa, agar perbandingannya adil.
NOMOR_INDEKS = 0


class IndexNetwork(jaringan.Network):
  """Jaringan dengan satu node indeks dan sejumlah node penanya."""

  nama = "client-server"

  def susun(self) -> None:
    """Menitipkan seluruh kunci kepada indeks lalu menyambungkan sisanya.

    Setiap node penanya hanya mengenal satu neighbor, yaitu indeksnya. Tidak
    ada satu pun sambungan antar penanya, sehingga jumlah sisinya sama dengan
    jumlah penanya.
    """
    simpul_indeks = self.simpul[NOMOR_INDEKS]
    for kunci in domain.daftar_kunci():
      simpul_indeks.simpan(kunci, domain.nilai_kurs(kunci))
    for nomor in range(self.jumlah_simpul):
      self.sambungkan(nomor, NOMOR_INDEKS)

  def cari(self, nomor_peminta: int, kunci: str) -> jaringan.LookupResult:
    """Bertanya satu kali kepada indeks, lalu menunggu satu jawaban.

    Mengembalikan LookupResult berisi dua pesan dan satu hop, berapa pun jumlah
    node-nya. Bila indeksnya mati, nilainya None dan lookup itu tidak
    pernah terjawab, sebab tidak ada node lain yang menyimpan salinannya.
    """
    peminta = self.simpul[nomor_peminta]
    if not peminta.hidup:
      return jaringan.LookupResult(kunci, None, 0, 0)
    nilai = peminta.ambil(kunci)
    if nilai is not None:
      return jaringan.LookupResult(kunci, nilai, 0, 0)
    # Satu pesan pertanyaan berangkat, lalu satu pesan jawaban kembali.
    nilai = self.simpul[NOMOR_INDEKS].ambil(kunci)
    return jaringan.LookupResult(kunci, nilai, 2, 1)


if __name__ == "__main__":
  jaringan_indeks = IndexNetwork(8)
  print(jaringan_indeks.ringkas())
  hasil = jaringan_indeks.cari(3, "EUR/IDR")
  print(f"Lookup EUR/IDR dari node 3 : {hasil}")
  jaringan_indeks.matikan(NOMOR_INDEKS)
  hasil = jaringan_indeks.cari(3, "EUR/IDR")
  print(f"Sesudah indeks dimatikan        : {hasil}")
  # Keluarannya: Sesudah indeks dimatikan        : LookupResult(EUR/IDR, nilai=None,
  # pesan=2, hop=1)
