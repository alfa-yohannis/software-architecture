"""Menghitung biaya dua jenis perubahan pada kedua versi aplikasi.

Perubahan pertama menambah satu fitur yang seluruhnya berada di dalam satu
bidang, yaitu ringkasan kurs. Perubahan kedua mengubah skema tabel pesanan
yang dipakai bersama, yaitu mengganti nama kolom nominal menjadi
nominal_asing. Keduanya sengaja dipilih berlawanan, sebab yang pertama
menguntungkan pemecahan layanan sedangkan yang kedua menghukumnya.

Tiga angka dilaporkan untuk tiap perubahan pada tiap versi, yaitu berkas yang
berubah, baris yang berubah, dan proses yang harus dijalankan ulang. Baris
yang berubah dihitung sebagai jumlah baris yang dihapus ditambah baris yang
ditambahkan, mengikuti cara difflib membaca selisih. Proses yang harus
dijalankan ulang dihitung dari pernyataan import setiap proses, bukan
dikira-kira, sehingga berkas yang dimuat lebih dari satu proses ikut
terlihat.

Naskah kode yang ada tidak disentuh sama sekali. Perubahannya diterapkan pada
salinan di dalam memori, lalu hasilnya diperiksa dengan compile agar angka
yang dilaporkan berasal dari kode yang benar-benar sah.

Cara menjalankan: python biaya_perubahan.py
"""

import ast
import difflib
import pathlib

import jalankan_layanan

DIREKTORI = pathlib.Path(__file__).resolve().parent

# Fungsi baru yang disisipkan ke dalam bidang kurs pada perubahan pertama.
FUNGSI_RINGKAS = '''

def hitung_rata_rata() -> dict:
  """Menghitung rata-rata seluruh nilai tukar yang tersimpan.

  Dipakai halaman ringkasan yang menampilkan gambaran kasar nilai rupiah
  terhadap mata uang yang dilayani. Mengembalikan dict berisi jumlah mata
  uang dan rata-rata nilainya.
  """
  daftar = daftar_kurs()
  jumlah = sum(satu["nilai"] for satu in daftar)
  return {"jumlah_mata_uang": len(daftar), "rata_rata": jumlah / len(daftar)}'''

JALUR_RINGKAS = '''@aplikasi.get("/kurs-ringkas")
def baca_kurs_ringkas() -> dict:
  """Melayani permintaan ringkasan seluruh nilai tukar yang tersimpan.

  Mengembalikan dict berisi jumlah mata uang, rata-rata nilainya, dan jumlah
  lompatan jaringan permintaan ini.
  """
  hasil = domain_kurs.hitung_rata_rata()
  hasil["lompatan"] = alamat.{lompatan}
  return hasil


'''

PENUTUP_DAFTAR_KURS = (
  '  return [{"kode": satu["kode"], "nilai": satu["nilai"]} for satu in baris]')

PERUBAHAN = (
  {
    "judul": "Menambah fitur ringkasan kurs di dalam satu bidang",
    "bersama": (
      ("domain_kurs.py", PENUTUP_DAFTAR_KURS,
       PENUTUP_DAFTAR_KURS + FUNGSI_RINGKAS),
    ),
    "monolit": (
      ("monolit.py", '@aplikasi.get("/pesanan/<int:nomor>")',
       JALUR_RINGKAS.format(lompatan="LOMPATAN_KLIEN")
       + '@aplikasi.get("/pesanan/<int:nomor>")'),
    ),
    "layanan": (
      ("layanan_kurs.py", 'if __name__ == "__main__":',
       JALUR_RINGKAS.format(lompatan="LOMPATAN_LAYANAN")
       + 'if __name__ == "__main__":'),
    ),
  },
  {
    "judul": "Mengganti nama kolom nominal pada tabel pesanan bersama",
    "bersama": (
      ("basis_data.py",
       "  nominal    REAL NOT NULL,",
       "  nominal_asing  REAL NOT NULL,"),
      ("basis_data.py",
       "INSERT INTO pesanan (nomor, pelanggan, mata_uang, nominal, status)",
       "INSERT INTO pesanan"
       " (nomor, pelanggan, mata_uang, nominal_asing, status)"),
      ("domain_pemesanan.py",
       "SELECT nomor, pelanggan, mata_uang, nominal, status\n"
       "FROM pesanan\nWHERE nomor = ?",
       "SELECT nomor, pelanggan, mata_uang, nominal_asing, status\n"
       "FROM pesanan\nWHERE nomor = ?"),
      ("domain_pemesanan.py",
       "SELECT nomor, pelanggan, mata_uang, nominal, status\n"
       "FROM pesanan\nORDER BY nomor",
       "SELECT nomor, pelanggan, mata_uang, nominal_asing, status\n"
       "FROM pesanan\nORDER BY nomor"),
      ("domain_pemesanan.py",
       '    "nominal": baris["nominal"],',
       '    "nominal": baris["nominal_asing"],'),
      ("domain_pemesanan.py",
       '      "nominal": satu["nominal"],',
       '      "nominal": satu["nominal_asing"],'),
      ("domain_penagihan.py",
       "SELECT nomor, nominal, status",
       "SELECT nomor, nominal_asing, status"),
      ("domain_penagihan.py",
       '    nominal_rupiah = round(baris["nominal"] * nilai_kurs,'
       " PEMBULATAN_RUPIAH)",
       '    nominal_rupiah = round(baris["nominal_asing"] * nilai_kurs,'
       " PEMBULATAN_RUPIAH)"),
    ),
    "monolit": (),
    "layanan": (),
  },
)


def baca_berkas(nama: str) -> str:
  """Membaca satu berkas sumber sebagai teks.

  Pembacaan dipisahkan agar berkas yang sama tidak dibuka berulang kali
  ketika satu perubahan menyentuh beberapa baris di dalamnya. Mengembalikan
  str berisi seluruh isi berkasnya.
  """
  return (DIREKTORI / nama).read_text(encoding="utf-8")


def terapkan(operasi: tuple) -> dict:
  """Menerapkan sederet penggantian teks pada salinan di dalam memori.

  Setiap teks lama wajib muncul tepat satu kali, dan pelanggaran atasnya
  melempar ValueError. Pemeriksaan itu mencegah angka nol yang muncul hanya
  karena polanya tidak ditemukan. Mengembalikan dict berisi pasangan nama
  berkas dan isi barunya.
  """
  hasil = {}
  for nama, lama, baru in operasi:
    isi = hasil.get(nama, baca_berkas(nama))
    if isi.count(lama) != 1:
      raise ValueError(f"pola pada {nama} muncul {isi.count(lama)} kali")
    hasil[nama] = isi.replace(lama, baru)
  for nama, isi in hasil.items():
    compile(isi, nama, "exec")
  return hasil


def hitung_baris_berubah(lama: str, baru: str) -> int:
  """Menghitung baris yang berbeda antara isi lama dan isi baru.

  Baris yang dihapus dan baris yang ditambahkan sama-sama dihitung, sebab
  keduanya menuntut pembacaan ulang oleh penulis kodenya. Mengembalikan int
  berisi jumlah baris yang berubah.
  """
  beda = difflib.unified_diff(lama.splitlines(), baru.splitlines(), n=0)
  return sum(1 for baris in beda
             if baris[:1] in ("+", "-") and baris[:3] not in ("+++", "---"))


def modul_diimpor(nama: str) -> set:
  """Membaca pernyataan import satu berkas tanpa menjalankannya.

  Pembacaan memakai ast, sebab mengimpor modulnya berarti menyalakan aplikasi
  Flask di dalamnya. Hanya modul yang berkasnya ada di direktori ini yang
  dihitung. Mengembalikan set berisi nama berkas modul lokal yang diimpor.
  """
  pohon = ast.parse(baca_berkas(nama))
  tetangga = set()
  for simpul in ast.walk(pohon):
    if isinstance(simpul, ast.Import):
      tetangga.update(satu.name for satu in simpul.names)
    elif isinstance(simpul, ast.ImportFrom) and simpul.module:
      tetangga.add(simpul.module)
  return {f"{satu}.py" for satu in tetangga
          if (DIREKTORI / f"{satu}.py").exists()}


def berkas_proses(masuk: str) -> set:
  """Menelusuri seluruh berkas yang dimuat satu proses, termasuk tak langsung.

  Penelusuran dilakukan berjenjang, sehingga basis_data.py ikut terhitung
  sebagai berkas layanan kurs walaupun layanan itu hanya mengimpor
  domain_kurs.py. Mengembalikan set berisi nama berkas yang dimuat proses
  tersebut.
  """
  terkumpul = {masuk}
  antrean = [masuk]
  while antrean:
    for tetangga in modul_diimpor(antrean.pop()):
      if tetangga not in terkumpul:
        terkumpul.add(tetangga)
        antrean.append(tetangga)
  return terkumpul


def proses_terdampak(daftar_proses: dict, berubah: set) -> list:
  """Menentukan proses mana yang memuat salah satu berkas yang berubah.

  Proses yang memuat berkas berubah wajib dijalankan ulang, walaupun
  perilakunya sendiri belum tentu berbeda. Mengembalikan list berisi nama
  proses yang harus dijalankan ulang, terurut menurut nama.
  """
  terdampak = [nama for nama, (berkas, _) in daftar_proses.items()
               if berkas_proses(berkas) & berubah]
  return sorted(terdampak)


def ukur_versi(perubahan: dict, kunci: str, daftar_proses: dict) -> dict:
  """Menghitung ketiga angka biaya satu perubahan pada satu versi.

  Operasi bersama digabung dengan operasi khusus versi itu, sebab modul
  domainnya memang dipakai kedua versi. Mengembalikan dict berisi jumlah
  berkas, jumlah baris, daftar proses yang dijalankan ulang, dan nama berkas
  yang berubah.
  """
  operasi = perubahan["bersama"] + perubahan[kunci]
  hasil = terapkan(operasi)
  baris = sum(hitung_baris_berubah(baca_berkas(nama), isi)
              for nama, isi in hasil.items())
  return {
    "berkas": len(hasil),
    "baris": baris,
    "proses": proses_terdampak(daftar_proses, set(hasil)),
    "nama_berkas": sorted(hasil),
  }


def cetak_versi(judul: str, hasil: dict, jumlah_proses: int) -> None:
  """Mencetak satu baris laporan untuk satu versi aplikasi.

  Label yang dicetak sama dengan istilah pada naskah bab, sebab langkah
  latihan menyuruh mahasiswa menyalin baris ini ke dalam tabel. Tidak
  mengembalikan apa pun.
  """
  print(f"  {judul:<14} berkas {hasil['berkas']}"
        f"   baris {hasil['baris']:2d}"
        f"   proses ulang {len(hasil['proses'])} dari {jumlah_proses}")


if __name__ == "__main__":
  for nomor, satu_perubahan in enumerate(PERUBAHAN, start=1):
    hasil_monolit = ukur_versi(satu_perubahan, "monolit",
                               jalankan_layanan.PROSES_MONOLIT)
    hasil_layanan = ukur_versi(satu_perubahan, "layanan",
                               jalankan_layanan.PROSES_LAYANAN)
    print(f"Perubahan {nomor}: {satu_perubahan['judul']}")
    cetak_versi("Monolit", hasil_monolit,
                len(jalankan_layanan.PROSES_MONOLIT))
    cetak_versi("Service-based", hasil_layanan,
                len(jalankan_layanan.PROSES_LAYANAN))
    print(f"  Berkas berubah : {', '.join(hasil_layanan['nama_berkas'])}")
    print(f"  Proses ulang   : {', '.join(hasil_layanan['proses'])}")
  # Keluarannya: Proses ulang   : kurs, pemesanan, penagihan
