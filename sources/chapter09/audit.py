"""Pelanggan baru yang disisipkan pada Latihan 3, yaitu pencatat audit.

Berkas ini berdiri sendiri dan tidak diimpor oleh satu pun susunan bawaan.
Ketiga berkas di dalam varian_audit/ adalah salinan susunan yang sudah
menyisipkannya, dan skrip ukur_perubahan.py menghitung selisih baris antara
keduanya.

Pemroses ini sengaja menyalin permintaan apa adanya, tanpa mengubah satu pun
isinya, sebab tugas audit memang hanya merekam. Ketiadaan perubahan itu pula
yang membuatnya aman dijalankan berbarengan dengan pemroses lain.

Cara menjalankan: python audit.py
"""

import threading

import domain

# Baris jurnal disimpan dalam memori saja, sama seperti riwayat pada Pencatat,
# agar latihan tidak membutuhkan basis data.
AWALAN_JURNAL = "AUDIT"


class PencatatAudit:
  """Perekam jurnal audit bagi setiap permintaan yang masuk.

  Pemroses ini tidak mengubah isi permintaan sama sekali. Tuntutannya hanya
  satu, yaitu tidak ada permintaan yang boleh lewat tanpa tercatat, sehingga
  jurnalnya dapat dibandingkan dengan riwayat pencatat bila terjadi selisih.
  """

  nama = "audit"

  def __init__(self) -> None:
    """Menyiapkan jurnal kosong beserta kunci yang menjaga penambahannya."""
    self.jurnal = []
    self.kunci = threading.Lock()

  def tangani(self, permintaan: domain.Permintaan) -> str:
    """Menyalin permintaan menjadi satu baris jurnal, lalu menandai langkahnya.

    Mengembalikan str berisi baris jurnal yang baru saja disimpan, sehingga
    pemanggil dapat memeriksanya tanpa membuka seluruh jurnal.
    """
    baris = (f"{AWALAN_JURNAL};{permintaan.nomor};{permintaan.kode_asal};"
             f"{permintaan.nominal:.2f}")
    with self.kunci:
      self.jurnal.append(baris)
    permintaan.catat_langkah(self.nama)
    return baris


if __name__ == "__main__":
  contoh = domain.buat_permintaan(31, 1)
  pencatat_audit = PencatatAudit()
  print(pencatat_audit.tangani(contoh))
  # Keluarannya: AUDIT;31;USD;32000.00
