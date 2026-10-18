"""Tuple space, yaitu memori tempat komponen bertukar data tanpa saling mengenal.

Gagasannya diambil dari Linda. Satu pihak menulis tupel ke ruang, lalu pihak lain
mengambil atau membacanya. Penulis tidak perlu tahu siapa pengambilnya, dan
keduanya tidak perlu hidup pada waktu yang sama.

Kelas Ruang dipakai dalam dua peran. Sebagai ruang bersama, satu objeknya
dipegang proses middleware lalu dipakai seluruh unit lewat proksi. Sebagai grid
memori, setiap processing unit memegang objeknya sendiri berisi salinan kurs.

Cara menjalankan: python ruang.py
"""

import collections
import threading
import time

# Nilai None pada pola berarti kolom tersebut boleh berisi apa saja.
SEMBARANG = None
BATAS_TUNGGU_CONTOH = 0.2


def cocok(tupel: tuple, pola: tuple) -> bool:
  """Memeriksa apakah sebuah tupel memenuhi pola.

  Kolom pola yang berisi SEMBARANG menerima isi apa pun, sedangkan kolom lain
  harus sama persis. Panjang keduanya juga harus sama, sehingga tupel kurs tidak
  pernah tertukar dengan tupel tugas. Mengembalikan True bila tupel memenuhi pola.
  """
  if len(tupel) != len(pola):
    return False
  for harapan, isi in zip(pola, tupel):
    if harapan is not SEMBARANG and harapan != isi:
      return False
  return True


class Ruang:
  """Tuple space dengan tiga operasi Linda, yaitu tulis, ambil, dan baca.

  Seluruh operasi dijaga satu kunci, sehingga pengambilan bersifat atomis. Bila
  dua pengambil berebut satu tupel, satu pengambil mendapatkannya dan yang lain
  tidak. Tupel dikelompokkan menurut kolom pertamanya, yaitu nama tupel, agar
  pencarian tugas tidak perlu memeriksa ribuan tupel jawaban.
  """

  def __init__(self) -> None:
    """Menyiapkan tempat tupel yang masih kosong beserta kunci penjaganya.

    Kunci dibungkus Condition agar pengambil yang belum menemukan tupel dapat
    tidur, lalu dibangunkan ketika ada tupel baru yang ditulis.
    """
    self.isi = collections.defaultdict(collections.deque)
    self.kondisi = threading.Condition(threading.Lock())

  def tulis(self, tupel: tuple) -> None:
    """Menambahkan satu tupel, lalu membangunkan seluruh pihak yang menunggu.

    Tupel yang sudah ditulis hidup sendiri di dalam ruang sampai ada yang
    mengambilnya, walaupun penulisnya sudah selesai. Tidak mengembalikan apa pun.
    """
    with self.kondisi:
      self.isi[tupel[0]].append(tupel)
      self.kondisi.notify_all()

  def ambil(self, pola: tuple, batas_waktu: float | None = None) -> tuple | None:
    """Mengeluarkan satu tupel yang memenuhi pola dari ruang.

    Bila belum ada yang cocok, pemanggil menunggu sampai ada atau sampai batas
    waktu habis. Tanpa batas waktu, penantiannya tidak berujung, persis seperti
    in() pada Linda. Mengembalikan tuple yang diambil, atau None bila batas waktu
    habis lebih dahulu.
    """
    return self._tunggu_cocok(pola, True, batas_waktu)

  def baca(self, pola: tuple, batas_waktu: float | None = None) -> tuple | None:
    """Membaca satu tupel yang memenuhi pola tanpa mengeluarkannya.

    Aturan menunggunya sama dengan ambil. Karena tupel tetap tinggal, banyak
    pembaca dapat membaca tupel yang sama. Mengembalikan tuple yang dibaca, atau
    None bila batas waktu habis lebih dahulu.
    """
    return self._tunggu_cocok(pola, False, batas_waktu)

  def baca_semua(self, pola: tuple) -> list[tuple]:
    """Membaca seluruh tupel yang memenuhi pola tanpa menunggu.

    Dipakai processing unit saat mulai untuk menyalin seluruh kurs sekaligus ke
    grid memorinya. Mengembalikan list berisi tupel yang cocok, kosong bila tidak
    ada.
    """
    with self.kondisi:
      return [tupel for tupel in self.isi.get(pola[0], ()) if cocok(tupel, pola)]

  def hitung(self, pola: tuple) -> int:
    """Menghitung tupel yang memenuhi pola tanpa mengubah isi ruang.

    Mengembalikan int berisi jumlah tupel yang cocok.
    """
    with self.kondisi:
      return sum(1 for tupel in self.isi.get(pola[0], ()) if cocok(tupel, pola))

  def _tunggu_cocok(self, pola: tuple, keluarkan: bool,
                    batas_waktu: float | None) -> tuple | None:
    """Mencari tupel yang cocok, lalu tidur selama belum ada yang cocok.

    Pencarian dan pengeluaran terjadi di bawah kunci yang sama, sehingga tidak
    ada celah bagi pengambil lain di antara keduanya. Mengembalikan tuple yang
    ditemukan, atau None bila batas waktu habis.
    """
    tenggat = None if batas_waktu is None else time.monotonic() + batas_waktu
    with self.kondisi:
      while True:
        tupel = self._cari(pola, keluarkan)
        if tupel is not None:
          return tupel
        if tenggat is None:
          self.kondisi.wait()
          continue
        sisa = tenggat - time.monotonic()
        if sisa <= 0:
          return None
        self.kondisi.wait(sisa)

  def _cari(self, pola: tuple, keluarkan: bool) -> tuple | None:
    """Menelusuri tupel senama dari yang paling lama ditulis.

    Linda tidak menjanjikan tupel mana yang diberikan bila ada beberapa yang
    cocok. Kelas ini memilih yang paling lama, sehingga tugas dikerjakan kurang
    lebih sesuai urutan kedatangannya. Mengembalikan tuple yang cocok atau None.
    """
    antrean = self.isi.get(pola[0])
    if not antrean:
      return None
    for letak, tupel in enumerate(antrean):
      if cocok(tupel, pola):
        if keluarkan:
          del antrean[letak]
        return tupel
    return None


def ambil_untuk_contoh(ruang: Ruang, hasil: list) -> None:
  """Mengambil satu tugas dengan batas waktu, lalu mencatat apa yang diperoleh.

  Fungsi ini dijalankan dua thread sekaligus pada contoh di bawah, agar terlihat
  bahwa satu tupel tidak mungkin diperoleh dua pengambil. Tidak mengembalikan
  apa pun, sebab hasilnya dicatat ke list yang diberikan.
  """
  hasil.append(ruang.ambil(("tugas", None), BATAS_TUNGGU_CONTOH))


if __name__ == "__main__":
  ruang_contoh = Ruang()
  ruang_contoh.tulis(("tugas", 1))
  perolehan = []
  pengambil = [threading.Thread(target=ambil_untuk_contoh,
                                args=(ruang_contoh, perolehan))
               for _ in range(2)]
  for benang in pengambil:
    benang.start()
  for benang in pengambil:
    benang.join()
  dapat = sum(1 for tupel in perolehan if tupel is not None)
  print(f"Pengambil yang mendapat tupel : {dapat} dari {len(pengambil)}")
  # Keluarannya: Pengambil yang mendapat tupel : 1 dari 2

  pola_kurs = ("kurs", "USD", "IDR", SEMBARANG, SEMBARANG)
  ruang_contoh.tulis(("kurs", "USD", "IDR", 16250.0, 1))
  ruang_contoh.baca(pola_kurs)
  ruang_contoh.baca(pola_kurs)
  print(f"Tupel kurs sesudah dua kali baca: {ruang_contoh.hitung(pola_kurs)}")
  # Keluarannya: Tupel kurs sesudah dua kali baca: 1
