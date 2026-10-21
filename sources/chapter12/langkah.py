"""Tujuh langkah bisnis yang dipakai bersama oleh kedua versi Bab 12.

Berkas ini memuat satu-satunya salinan aturan bisnisnya. Versi orkestrasi dan
versi tanpa orkestrasi sama-sama memanggil fungsi di sini, sehingga selisih
yang diukur pada bab ini benar-benar selisih cara merangkai, bukan selisih isi
langkahnya.

Setiap fungsi menerima konteks alur kerja berupa dict, lalu mengembalikan dict
berisi tambahan untuk konteks itu. Bentuk seperti itu membuat langkah dapat
disusun ulang tanpa mengubah tanda tangannya, dan membuat mesin orkestrasi
dapat menyimpan konteks di antara dua langkah.

Cara menjalankan: python langkah.py
"""

import threading

import data

# Nomor transaksi dan nomor audit dibentuk dari panjang bukunya, sehingga
# penambahannya wajib dilindungi kunci. Server melayani setiap permintaan pada
# utasnya sendiri.
KUNCI_BUKU = threading.Lock()

# Nominal bawaan bagi alur kerja yang hanya membaca kurs tanpa memesan apa pun.
NOMINAL_BAWAAN = 1.0


class LangkahGagal(Exception):
  """Ditandai ketika sebuah langkah ditolak oleh aturan bisnisnya.

  Galat ini berbeda dengan galat jaringan. Galat bisnis berarti alur kerjanya
  memang tidak boleh dilanjutkan, sedangkan galat jaringan berarti alur
  kerjanya layak diulang setelah layanannya hidup kembali.
  """


def periksa_nasabah(konteks: dict) -> dict:
  """Memastikan nasabah terdaftar dan rekeningnya masih aktif.

  Langkah ini menjadi penjaga pertama seluruh alur kerja, sebab langkah
  sesudahnya memotong saldo dan mencatat transaksi atas nama nasabah tersebut.
  Mengembalikan dict berisi nama nasabah dan pagu hariannya.
  """
  nomor = konteks.get("nasabah")
  catatan = data.DAFTAR_NASABAH.get(nomor)
  if catatan is None:
    raise LangkahGagal(f"nasabah {nomor} tidak terdaftar")
  if not catatan["aktif"]:
    raise LangkahGagal(f"nasabah {nomor} tidak aktif")
  return {"nama_nasabah": catatan["nama"], "pagu_harian": catatan["pagu_harian"]}


def ambil_kurs(konteks: dict) -> dict:
  """Mengambil kurs jual satu mata uang lalu menghitung nilai rupiahnya.

  Kurs jual adalah kurs dasar ditambah margin bank. Margin tambahan dibaca dari
  data setiap kali langkah ini dipanggil, sebab skrip pemakaian ulang mengubah
  angka itu di tengah jalan. Mengembalikan dict berisi kurs dasar, margin, kurs
  jual, dan nilai rupiah pesanan.
  """
  kode = konteks.get("mata_uang")
  catatan = data.DAFTAR_KURS.get(kode)
  if catatan is None:
    raise LangkahGagal(f"mata uang {kode} tidak dilayani")
  margin = catatan["margin"] + data.MARGIN_TAMBAHAN
  kurs_jual = catatan["dasar"] + margin
  nominal = float(konteks.get("nominal", NOMINAL_BAWAAN))
  return {
    "kurs_dasar": catatan["dasar"],
    "margin": margin,
    "kurs_jual": kurs_jual,
    "rupiah": round(nominal * kurs_jual, 2),
  }


def periksa_batas_harian(konteks: dict) -> dict:
  """Menolak pesanan yang membuat pemakaian harian melewati pagu nasabah.

  Langkah ini membaca pagu yang sudah diletakkan langkah nasabah ke dalam
  konteks, sehingga urutannya tidak boleh mendahului langkah tersebut.
  Mengembalikan dict berisi jumlah rupiah yang terpakai hari itu.
  """
  nomor = konteks.get("nasabah")
  rupiah = float(konteks.get("rupiah", 0.0))
  pagu = float(konteks.get("pagu_harian", 0.0))
  terpakai = data.TERPAKAI_HARIAN.get(nomor, 0.0) + rupiah
  if terpakai > pagu:
    raise LangkahGagal(f"pesanan melewati pagu harian {pagu:,.0f} rupiah")
  data.TERPAKAI_HARIAN[nomor] = terpakai
  return {"terpakai_harian": terpakai}


def potong_saldo(konteks: dict) -> dict:
  """Mengurangi saldo rupiah nasabah sebesar nilai pesanannya.

  Inilah satu-satunya langkah yang mengubah uang, sehingga kegagalan sesudah
  langkah ini menuntut pembatalan, bukan sekadar pengulangan. Mengembalikan
  dict berisi sisa saldo nasabah.
  """
  nomor = konteks.get("nasabah")
  rupiah = float(konteks.get("rupiah", 0.0))
  tersedia = data.SALDO.get(nomor)
  if tersedia is None:
    raise LangkahGagal(f"rekening {nomor} tidak ditemukan")
  if tersedia < rupiah:
    raise LangkahGagal(f"saldo {tersedia:,.0f} kurang dari {rupiah:,.0f}")
  data.SALDO[nomor] = tersedia - rupiah
  return {"saldo_sisa": data.SALDO[nomor]}


def catat_transaksi(konteks: dict) -> dict:
  """Menulis satu baris pesanan ke buku transaksi bersama.

  Nomor transaksinya dibentuk berurutan, sebab nomor itulah yang dipakai bukti
  dan jejak audit sesudahnya. Mengembalikan dict berisi nomor transaksi.
  """
  with KUNCI_BUKU:
    nomor = f"TRX-{len(data.BUKU_TRANSAKSI) + 1:06d}"
    data.BUKU_TRANSAKSI.append({
      "nomor": nomor,
      "nasabah": konteks.get("nasabah"),
      "alur": konteks.get("alur"),
      "rupiah": konteks.get("rupiah", 0.0),
    })
  return {"nomor_transaksi": nomor}


def buat_bukti(konteks: dict) -> dict:
  """Menyusun teks bukti pemesanan valuta asing bagi nasabah.

  Langkah ini hanya dipakai satu alur kerja, sehingga menjadi contoh layanan
  aplikasi pada taksonomi bab ini. Mengembalikan dict berisi satu baris bukti
  siap cetak.
  """
  baris = (f"{konteks.get('nomor_transaksi')} "
           f"{konteks.get('nominal')} {konteks.get('mata_uang')} "
           f"@ {konteks.get('kurs_jual'):,.0f} = "
           f"{konteks.get('rupiah'):,.0f} rupiah")
  return {"bukti": baris}


def catat_audit(konteks: dict) -> dict:
  """Menyimpan jejak satu alur kerja yang selesai ke dalam catatan audit.

  Layanan ini dipakai seluruh alur kerja, sehingga menjadi contoh layanan
  infrastruktur pada taksonomi bab ini. Mengembalikan dict berisi nomor
  urut jejak audit yang baru ditulis.
  """
  with KUNCI_BUKU:
    data.JEJAK_AUDIT.append({
      "alur": konteks.get("alur"),
      "nasabah": konteks.get("nasabah"),
      "transaksi": konteks.get("nomor_transaksi"),
    })
    nomor = len(data.JEJAK_AUDIT)
  return {"nomor_audit": nomor}


# Peta dari nama langkah ke fungsinya. Mesin orkestrasi maupun layanan berantai
# mencari fungsinya lewat peta ini, sehingga nama langkah pada definisi alur
# kerja cukup ditulis sebagai teks.
FUNGSI = {
  "nasabah": periksa_nasabah,
  "kurs": ambil_kurs,
  "batas": periksa_batas_harian,
  "saldo": potong_saldo,
  "transaksi": catat_transaksi,
  "bukti": buat_bukti,
  "audit": catat_audit,
}


def jalankan_langkah(nama: str, konteks: dict) -> dict:
  """Menjalankan satu langkah berdasarkan namanya lalu mengembalikan hasilnya.

  Nama yang tidak dikenal dianggap galat bisnis, sebab definisi alur kerja yang
  menyebut langkah tak dikenal memang tidak boleh dijalankan. Mengembalikan
  dict berisi tambahan konteks dari langkah tersebut.
  """
  fungsi = FUNGSI.get(nama)
  if fungsi is None:
    raise LangkahGagal(f"langkah {nama} tidak dikenal")
  return fungsi(konteks)


if __name__ == "__main__":
  data.setel_ulang()
  konteks_uji = {"nasabah": "N001", "mata_uang": "USD", "nominal": 10.0,
                 "alur": "pesan-valas"}
  for nama_langkah in ["nasabah", "kurs", "saldo", "transaksi", "bukti"]:
    konteks_uji.update(jalankan_langkah(nama_langkah, konteks_uji))
  print(f"Langkah dijalankan: {len(konteks_uji)} kunci konteks")
  print(f"Bukti             : {konteks_uji['bukti']}")
  # Keluarannya: Bukti             : TRX-000001 10.0 USD @ 16,325 = 163,250 rupiah
