"""Susunan structured, yaitu cincin pengenal beserta finger table ala Chord.

Nama node dan nama key sama-sama dipetakan menjadi satu identifier pada
cincin oleh fungsi hash yang sama. Sebuah key dititipkan kepada successor-nya,
yaitu node pertama yang identifier-nya tidak mendahului identifier key itu.
Aturan tersebut membuat letak key dapat dihitung, bukan dicari, sehingga
pertanyaan tidak perlu disebar ke mana-mana.

Agar penelusurannya tidak sequential satu node demi satu node, setiap node
menyimpan finger table. Finger ke-i menunjuk successor dari identifier dirinya
ditambah dua pangkat i, sehingga satu hop dapat memangkas separuh sisa jarak.
Jumlah hop-nya karena itu tumbuh menurut logaritma jumlah node, sesuai
protokol Chord yang disusun Stoica dan kawan-kawan pada tahun 2001.

Ruang pengenalnya enam belas bit, yaitu 65536 identifier. Chord sungguhan
memakai seratus enam puluh bit agar dua node tidak pernah menempati identifier
yang sama.
Ruang yang lebih sempit dipilih di sini agar angkanya muat dibaca, dan enam
belas bit masih cukup lebar untuk ratusan node. Ruang delapan bit sudah
terbukti terlalu sempit, sebab dua di antara 32 node menempati identifier
sama lalu membuat satu dari lima lookup tidak terjawab.

Cara menjalankan: python cincin.py
"""

import hashlib
import operator

import domain
import jaringan

# Lebar ruang pengenal dalam bit. Jumlah baris finger table sama dengan angka ini.
BIT_PENGENAL = 16
RUANG_PENGENAL = 2 ** BIT_PENGENAL
# Batas hop sebagai pengaman, agar penelusuran tidak pernah berputar tanpa
# henti ketika sebagian node mati.
BATAS_LOMPATAN = BIT_PENGENAL + 1


def pengenal_dari(teks: str) -> int:
  """Memetakan sembarang teks menjadi satu identifier pada cincin.

  Mengembalikan bilangan bulat antara nol dan RUANG_PENGENAL dikurangi satu.
  SHA-1 dipakai, bukan fungsi hash bawaan Python, sebab hash bawaan diacak
  ulang pada setiap proses sehingga angkanya tidak dapat diulang.
  """
  sidik = hashlib.sha1(teks.encode("utf-8")).digest()
  return int.from_bytes(sidik, "big") % RUANG_PENGENAL


def nama_simpul(nomor: int) -> str:
  """Mengembalikan nama yang di-hash menjadi pengenal sebuah node.

  Chord sungguhan memakai alamat Internet Protocol beserta nomor portanya.
  Contoh bab ini memakai nomor node, sebab seluruh node-nya berada pada satu
  laptop yang sama.
  """
  return f"simpul-{nomor}"


def di_antara(titik: int, batas_bawah: int, batas_atas: int) -> bool:
  """Menentukan apakah satu identifier berada pada busur (batas_bawah, batas_atas].

  Pemeriksaannya berbeda dari perbandingan biasa sebab cincin melingkar, yaitu
  identifier 65535 bersebelahan dengan identifier 0. Busur yang melewati nol
  karena itu ditangani terpisah. Mengembalikan True bila identifier-nya berada
  di dalam busur tersebut.
  """
  if batas_bawah == batas_atas:
    return True
  if batas_bawah < batas_atas:
    return batas_bawah < titik <= batas_atas
  return titik > batas_bawah or titik <= batas_atas


class RingNode(jaringan.Node):
  """Node yang menempati satu identifier cincin dan menyimpan finger table-nya."""

  def __init__(self, nomor: int) -> None:
    """Menghitung identifier node lalu menyiapkan finger table yang masih kosong.

    Finger table-nya belum dapat diisi di sini, sebab isinya bergantung pada
    seluruh node lain yang mungkin belum dibuat.
    """
    super().__init__(nomor)
    self.pengenal = pengenal_dari(nama_simpul(nomor))
    self.jari = []

  def successor(self) -> int:
    """Mengembalikan nomor node successor, yaitu isi finger pertama."""
    return self.jari[0]


class RingNetwork(jaringan.Network):
  """Jaringan berbentuk cincin dengan penelusuran memakai finger table."""

  nama = "structured"

  def buat_simpul(self, nomor: int) -> RingNode:
    """Mengembalikan node yang sudah memegang pengenal cincinnya."""
    return RingNode(nomor)

  def susun(self) -> None:
    """Mengurutkan node pada cincin, mengisi finger table, lalu menitipkan key."""
    self.urutan = sorted(self.simpul, key=operator.attrgetter("pengenal"))
    self.periksa_pengenal_unik()
    self.isi_tabel_jari()
    self.titipkan_key()

  def periksa_pengenal_unik(self) -> None:
    """Memastikan tidak ada dua node yang menempati identifier cincin yang sama.

    Chord memang menganggap tabrakan identifier tidak mungkin terjadi, sebab
    ruangnya seratus enam puluh bit. Ruang yang lebih sempit membuat tabrakan
    itu mungkin, dan tabrakan yang dibiarkan akan menyesatkan penelusuran tanpa
    satu pun tanda. Karena itu tabrakan dihentikan di sini sebagai galat.
    """
    pengenal = [simpul.pengenal for simpul in self.urutan]
    if len(set(pengenal)) != len(pengenal):
      raise ValueError(f"Dua simpul menempati identifier cincin yang sama pada "
                       f"{self.jumlah_simpul} simpul, perlebar BIT_PENGENAL")

  def isi_tabel_jari(self) -> None:
    """Mengisi finger table setiap node beserta daftar neighbor-nya.

    Finger ke-i menunjuk successor dari identifier dirinya ditambah dua pangkat
    i. Nomor yang sama sering muncul berulang pada jaringan kecil, sebab jarak
    dua pangkat i sudah melampaui beberapa node sekaligus.
    """
    for simpul in self.simpul:
      simpul.jari = []
      for pangkat in range(BIT_PENGENAL):
        titik = (simpul.pengenal + 2 ** pangkat) % RUANG_PENGENAL
        simpul.jari.append(self.successor_titik(titik).nomor)
      simpul.tetangga = sorted(set(simpul.jari) - {simpul.nomor})

  def titipkan_key(self) -> None:
    """Menitipkan setiap key kepada successor identifier key-nya sendiri.

    Letaknya dapat dihitung ulang oleh node mana pun, dan justru itulah yang
    membedakan susunan ini dari susunan unstructured.
    """
    for key in domain.daftar_key():
      pemegang = self.successor_titik(pengenal_dari(key))
      pemegang.simpan(key, domain.nilai_kurs(key))

  def successor_titik(self, titik: int) -> RingNode:
    """Mengembalikan node pertama pada cincin yang tidak mendahului identifier itu.

    Pencariannya menyusuri urutan cincin dari awal, sebab jumlah node pada
    contoh bab ini kecil. Chord sungguhan tidak pernah memakai daftar lengkap
    seperti ini, sebab tidak ada node yang mengenal seluruh anggotanya.
    """
    for simpul in self.urutan:
      if simpul.pengenal >= titik:
        return simpul
    return self.urutan[0]

  def successor_hidup(self, simpul: RingNode):
    """Mengembalikan node hidup berikutnya pada cincin, atau None.

    Chord sungguhan menyediakan daftar successor cadangan agar penelusuran tetap
    jalan ketika successor terdekat mati, dan metode ini meniru daftar tersebut.
    """
    tempat = self.urutan.index(simpul)
    for geser in range(1, len(self.urutan)):
      calon = self.urutan[(tempat + geser) % len(self.urutan)]
      if calon.hidup:
        return calon
    return None

  def jari_terdekat(self, simpul: RingNode, sasaran: int):
    """Mengembalikan finger hidup terjauh yang belum melewati identifier sasaran.

    Finger terjauh dipilih agar satu hop memangkas sisa jarak sebanyak mungkin.
    Mengembalikan None bila tidak ada finger yang memenuhi syarat itu.
    """
    for pangkat in range(BIT_PENGENAL - 1, -1, -1):
      calon = self.simpul[simpul.jari[pangkat]]
      if not calon.hidup or calon.nomor == simpul.nomor:
        continue
      if di_antara(calon.pengenal, simpul.pengenal, sasaran):
        return calon
    return None

  def cari(self, nomor_peminta: int, key: str) -> jaringan.LookupResult:
    """Menelusuri cincin lewat finger table sampai successor pemegang key.

    Mengembalikan LookupResult berisi nilai kurs, jumlah hop, dan jumlah
    message sebanyak dua kali hop. Angka dua itu muncul sebab pertanyaan
    di-forward satu message per hop, lalu jawabannya pulang lewat jalur yang
    sama.
    """
    peminta = self.simpul[nomor_peminta]
    if not peminta.hidup:
      return jaringan.LookupResult(key, None, 0, 0)
    nilai = peminta.ambil(key)
    if nilai is not None:
      return jaringan.LookupResult(key, nilai, 0, 0)
    return self.telusuri(peminta, pengenal_dari(key), key)

  def telusuri(self, peminta: RingNode, sasaran: int, key: str):
    """Melompat dari satu node ke node berikutnya sampai sasaran tercapai.

    Mengembalikan LookupResult satu lookup. Nilainya None bila pemegang key-nya
    sudah mati, sebab tidak ada salinan key itu di node mana pun.
    """
    sekarang = peminta
    lompatan = 0
    while lompatan < BATAS_LOMPATAN:
      successor = self.successor_hidup(sekarang)
      if successor is None:
        break
      if di_antara(sasaran, sekarang.pengenal, successor.pengenal):
        lompatan += 1
        nilai = successor.ambil(key)
        return jaringan.LookupResult(key, nilai, lompatan * 2, lompatan)
      berikut = self.jari_terdekat(sekarang, sasaran) or successor
      sekarang = berikut
      lompatan += 1
    return jaringan.LookupResult(key, None, lompatan * 2, lompatan)


if __name__ == "__main__":
  jaringan_cincin = RingNetwork(8)
  print(jaringan_cincin.ringkas())
  for simpul_ini in jaringan_cincin.urutan:
    print(f"  node {simpul_ini.nomor} identifier {simpul_ini.pengenal:3d}"
          f" finger {simpul_ini.jari} key {len(simpul_ini.simpanan)}")
  print(f"Identifier key EUR/IDR : {pengenal_dari('EUR/IDR')}")
  hasil = jaringan_cincin.cari(3, "EUR/IDR")
  print(f"Lookup EUR/IDR dari node 3 : {hasil}")
  # Keluarannya: Lookup EUR/IDR dari node 3 : LookupResult(EUR/IDR,
  # nilai=20368.91, pesan=6, hop=3)
