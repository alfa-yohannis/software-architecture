"""Memeriksa susunan lapisan sebuah berkas aplikasi.

Skrip ini membaca kode tanpa menjalankannya, lalu melaporkan tiga hal. Pertama,
metode mana yang bersifat pass-through. Kedua, panggilan mana yang
melompati satu lapisan. Ketiga, jumlah metode pada setiap lapisan.

Setiap lapisan diwakili satu kelas, dan kolaborator sebuah kelas dikenali dari
anotasi tipe pada konstruktornya. Anotasi itulah yang membuat arah
ketergantungan dapat dibaca tanpa menjalankan satu baris pun kode aplikasi.

Cara menjalankan: python periksa_lapisan.py aplikasi_tertutup.py
"""

import ast
import sys

# Urutan lapisan dari atas ke bawah. Indeks dipakai untuk menghitung jarak
# lompatan antar lapisan.
URUTAN_LAPISAN = ["presentasi", "bisnis", "persistensi", "basis_data"]

# Selisih indeks dua atau lebih berarti ada lapisan yang dilewati.
JARAK_PELANGGARAN = 2


class PemeriksaLapisan:
  """Pembaca satu berkas aplikasi beserta laporan susunan lapisannya.

  Seluruh hasil urai disimpan sebagai atribut, sehingga ketiga pemeriksaan
  dapat dijalankan berulang tanpa membaca berkasnya lagi.
  """

  def __init__(self, nama_berkas):
    """Mengurai berkas menjadi pohon sintaks, lalu mengambil peta lapisannya.

    Berkas dibaca sebagai teks, bukan diimpor, sehingga pemeriksaan tidak
    menjalankan kode apa pun.
    """
    self.nama_berkas = nama_berkas
    with open(nama_berkas, encoding="utf-8") as berkas:
      self.pohon = ast.parse(berkas.read(), filename=nama_berkas)
    self.peta_lapisan = self.baca_peta_lapisan()
    self.kelas = self.kumpulkan_kelas()

  def baca_peta_lapisan(self):
    """Mengambil nilai konstanta LAPISAN dari pohon sintaks.

    Peta ini ditulis eksplisit di dalam berkas aplikasi, sehingga pemeriksaan
    tidak perlu menebak lapisan sebuah kelas dari namanya.
    """
    for simpul in self.pohon.body:
      if not isinstance(simpul, ast.Assign):
        continue
      for sasaran in simpul.targets:
        if isinstance(sasaran, ast.Name) and sasaran.id == "LAPISAN":
          return ast.literal_eval(simpul.value)
    raise ValueError("Berkas tidak memuat konstanta LAPISAN")

  def kumpulkan_kelas(self):
    """Mengumpulkan kelas tingkat modul yang namanya tercantum pada peta."""
    return {s.name: s for s in self.pohon.body
            if isinstance(s, ast.ClassDef) and s.name in self.peta_lapisan}

  def baca_anotasi(self, konstruktor):
    """Memetakan nama parameter konstruktor ke nama kelas pada anotasinya."""
    anotasi = {}
    for parameter in konstruktor.args.args:
      if isinstance(parameter.annotation, ast.Name):
        anotasi[parameter.arg] = parameter.annotation.id
    return anotasi

  def petakan_atribut(self, simpul_kelas):
    """Memetakan atribut hasil penugasan konstruktor ke kelas kolaboratornya.

    Pemetaan ini membuat panggilan seperti self.repositori.daftar_kurs_jual
    dapat ditelusuri sampai ke kelas tujuannya, lalu ke lapisannya.
    """
    peta = {}
    for anggota in simpul_kelas.body:
      if not isinstance(anggota, ast.FunctionDef) or anggota.name != "__init__":
        continue
      anotasi = self.baca_anotasi(anggota)
      for pernyataan in anggota.body:
        if not isinstance(pernyataan, ast.Assign):
          continue
        sasaran = pernyataan.targets[0]
        if not isinstance(sasaran, ast.Attribute):
          continue
        if not isinstance(sasaran.value, ast.Name) or sasaran.value.id != "self":
          continue
        if not isinstance(pernyataan.value, ast.Name):
          continue
        kelas_tujuan = anotasi.get(pernyataan.value.id)
        if kelas_tujuan is not None:
          peta[sasaran.attr] = kelas_tujuan
    return peta

  def kumpulkan_metode(self, simpul_kelas):
    """Mengumpulkan metode biasa, tanpa konstruktor dan metode bergaris bawah.

    Konstruktor tidak ikut dihitung sebab isinya hanya menyimpan kolaborator,
    bukan melayani request.
    """
    return {s.name: s for s in simpul_kelas.body
            if isinstance(s, ast.FunctionDef) and not s.name.startswith("__")}

  def apakah_pass_through(self, simpul_metode):
    """Menentukan apakah sebuah metode bersifat pass-through.

    Metode disebut pass-through bila tubuhnya, setelah docstring dilewati,
    hanya berisi satu pernyataan return yang isinya satu pemanggilan.
    """
    isi = [p for p in simpul_metode.body if not isinstance(p, ast.Expr)]
    if len(isi) != 1 or not isinstance(isi[0], ast.Return):
      return False
    return isinstance(isi[0].value, ast.Call)

  def panggilan_ke_kolaborator(self, simpul_metode, peta_atribut):
    """Mengumpulkan panggilan berbentuk self.atribut.metode di dalam metode.

    Panggilan ke kolaborator di luar susunan lapisan, misalnya penjaga akses,
    ikut terkumpul lalu diabaikan saat lapisannya tidak dikenali.
    """
    temuan = []
    for anak in ast.walk(simpul_metode):
      if not isinstance(anak, ast.Call):
        continue
      if not isinstance(anak.func, ast.Attribute):
        continue
      pemilik = anak.func.value
      if not isinstance(pemilik, ast.Attribute):
        continue
      if not isinstance(pemilik.value, ast.Name) or pemilik.value.id != "self":
        continue
      kelas_tujuan = peta_atribut.get(pemilik.attr)
      if kelas_tujuan is not None:
        temuan.append((kelas_tujuan, anak.func.attr))
    return temuan

  def daftar_metode(self):
    """Mengembalikan seluruh metode berlapis sebagai daftar tupel bernama."""
    daftar = []
    for nama_kelas, simpul_kelas in self.kelas.items():
      for nama_metode, simpul in self.kumpulkan_metode(simpul_kelas).items():
        daftar.append((nama_kelas, nama_metode, simpul))
    return daftar

  def cari_pass_through(self):
    """Mengumpulkan nama metode yang bersifat pass-through."""
    return [f"{kelas}.{metode}" for kelas, metode, simpul in self.daftar_metode()
            if self.apakah_pass_through(simpul)]

  def cari_lompatan(self):
    """Mencari panggilan yang melompati satu lapisan atau lebih.

    Lompatan dihitung dari selisih indeks lapisan pemanggil dan lapisan yang
    dipanggil. Selisih satu berarti wajar, selisih dua atau lebih berarti ada
    lapisan yang dilewati.
    """
    temuan = []
    for nama_kelas, simpul_kelas in self.kelas.items():
      lapis_asal = self.peta_lapisan[nama_kelas]
      peta_atribut = self.petakan_atribut(simpul_kelas)
      for nama_metode, simpul in self.kumpulkan_metode(simpul_kelas).items():
        for kelas_tujuan, metode_tujuan in self.panggilan_ke_kolaborator(
            simpul, peta_atribut):
          lapis_tujuan = self.peta_lapisan.get(kelas_tujuan)
          if lapis_tujuan is None:
            continue
          jarak = (URUTAN_LAPISAN.index(lapis_tujuan)
                   - URUTAN_LAPISAN.index(lapis_asal))
          if jarak >= JARAK_PELANGGARAN:
            temuan.append((f"{nama_kelas}.{nama_metode}", lapis_asal,
                           f"{kelas_tujuan}.{metode_tujuan}", lapis_tujuan))
    return temuan

  def laporkan(self):
    """Mencetak ketiga hasil pemeriksaan untuk satu berkas aplikasi."""
    metode = self.daftar_metode()
    pass_through = self.cari_pass_through()
    bagian = 100 * len(pass_through) / len(metode) if metode else 0.0

    print(f"Berkas: {self.nama_berkas}")
    print(f"  Kelas berlapis         : {len(self.kelas)}")
    print(f"  Jumlah metode berlapis : {len(metode)}")
    print(f"  Metode pass-through    : {len(pass_through)}"
          f" {sorted(pass_through)}")
    print(f"  Bagian pass-through    : {bagian:.1f} persen")
    print(f"  Metode bekerja         : {len(metode) - len(pass_through)}")

    lompatan = self.cari_lompatan()
    print(f"  Layer violation        : {len(lompatan)}")
    for pemanggil, asal, tujuan, lapis_tujuan in lompatan:
      print(f"    {pemanggil} ({asal}) memanggil {tujuan} ({lapis_tujuan})")


if __name__ == "__main__":
  PemeriksaLapisan(sys.argv[1]).laporkan()
  # Keluarannya: Metode pass-through    : 1 ['LayananKurs.susun_kurs_dasar']
