"""Salinan tahap penggabungan peringkat milik Exim, agar dapat diukur sendirian.

Isi berkas ini disalin dari kelas ReciprocalRankFusion pada
https://github.com/alfa-yohannis/exim, berkas app/retrieval.py. Yang diubah
hanya satu, yaitu RetrievedPassage diganti dataclass kecil di berkas ini,
sehingga pengukuran berjalan tanpa memasang PyTorch, FastAPI, maupun model
apa pun.

Tahap ini dipilih sebab berada di jalur panas setiap pertanyaan, tidak
menyentuh jaringan, dan tidak memerlukan korpus. Karena itu keadaan awalnya
dapat diukur di laptop mana pun, lalu dibandingkan dengan keadaan sesudah
diubah.

Cara penggabungannya memakai reciprocal rank fusion, yaitu tiap daftar
menyumbang satu per k ditambah peringkat. Konstanta k meredam pengaruh
peringkat teratas, sehingga satu metode pencarian tidak mendominasi hasil
gabungan.

Cara menjalankan: python tahap_penggabungan.py
"""

import dataclasses

# Konstanta peredam pada reciprocal rank fusion. Nilai 60 dipakai Exim, dan
# angka itu pula yang lazim pada pustaka pencarian hibrida.
KONSTANTA_PEREDAM = 60


@dataclasses.dataclass
class Potongan:
  """Satu potongan teks hasil pencarian beserta skor yang menyertainya.

  Bentuknya dipersempit dari RetrievedPassage milik Exim, yaitu hanya kolom
  yang benar-benar disentuh tahap penggabungan. Kolom skor dipisah, bukan
  dilebur, sebab antarmuka Exim perlu menerangkan mengapa satu potongan muncul.
  """

  chunk_id: int
  skor_vektor: float = None
  skor_kata: float = None
  skor_gabungan: float = 0.0


def kunci_skor_gabungan(potongan: Potongan) -> float:
  """Mengembalikan float berisi skor gabungan, dipakai sebagai kunci urut."""
  return potongan.skor_gabungan


def gabungkan_skor(sasaran: Potongan, lain: Potongan) -> None:
  """Menyalin skor yang belum dimiliki sasaran dari potongan kembarnya.

  Satu potongan dapat muncul pada dua daftar sekaligus, dan skor dari kedua
  metode pencarian itu perlu disimpan keduanya. Tidak mengembalikan apa pun.
  """
  if sasaran.skor_vektor is None and lain.skor_vektor is not None:
    sasaran.skor_vektor = lain.skor_vektor
  if sasaran.skor_kata is None and lain.skor_kata is not None:
    sasaran.skor_kata = lain.skor_kata


def gabungkan_peringkat(daftar_terurut: list,
                        peredam: int = KONSTANTA_PEREDAM) -> list:
  """Menggabungkan beberapa daftar peringkat menjadi satu peringkat sepakat.

  Potongan yang muncul di lebih dari satu daftar naik di atas potongan yang
  hanya disukai satu metode, sebab sumbangannya dijumlahkan. Mengembalikan
  list berisi Potongan, terurut menurun menurut skor gabungannya.
  """
  gabungan = {}
  for satu_daftar in daftar_terurut:
    for peringkat, potongan in enumerate(satu_daftar, start=1):
      sumbangan = 1.0 / (peredam + peringkat)
      sudah_ada = gabungan.get(potongan.chunk_id)
      if sudah_ada is None:
        potongan.skor_gabungan = sumbangan
        gabungan[potongan.chunk_id] = potongan
      else:
        sudah_ada.skor_gabungan += sumbangan
        gabungkan_skor(sudah_ada, potongan)
  hasil = list(gabungan.values())
  hasil.sort(key=kunci_skor_gabungan, reverse=True)
  return hasil


if __name__ == "__main__":
  daftar_vektor = [Potongan(nomor, skor_vektor=1.0) for nomor in (1, 2, 3)]
  daftar_kata = [Potongan(nomor, skor_kata=1.0) for nomor in (3, 4, 1)]
  hasil_contoh = gabungkan_peringkat([daftar_vektor, daftar_kata])
  print(f"Konstanta peredam   : {KONSTANTA_PEREDAM}")
  print(f"Kandidat masuk      : {len(daftar_vektor) + len(daftar_kata)}")
  print(f"Kandidat keluar     : {len(hasil_contoh)}")
  for potongan_contoh in hasil_contoh:
    print(f"  chunk {potongan_contoh.chunk_id}  "
          f"skor gabungan {potongan_contoh.skor_gabungan:.6f}  "
          f"vektor {potongan_contoh.skor_vektor}  "
          f"kata {potongan_contoh.skor_kata}")
  print("Potongan yang muncul di kedua daftar naik ke atas, sebab "
        "sumbangannya dijumlahkan.")
