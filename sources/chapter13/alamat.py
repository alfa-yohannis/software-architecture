"""Porta dan alamat seluruh proses Bab 13, disimpan di satu tempat.

Kedua versi yang dibandingkan bab ini dinyalakan berdampingan pada mesin yang
sama, sehingga port-nya tidak boleh bertabrakan. Versi monolit memakai satu
port saja, sedangkan versi mikroservis memakai empat, yaitu satu gerbang dan
tiga layanan. Semua skrip pengukuran mengambil alamatnya dari file ini, agar
perubahan port cukup dikerjakan sekali.

Seluruh proses hanya mendengarkan pada 127.0.0.1, sebab latihan ini dijalankan
di satu laptop dan tidak dimaksudkan menerima request dari jaringan luar.

File ini tidak dijalankan sendiri, melainkan diimpor modul lain.
"""

INDUK = "http://127.0.0.1"

PORTA_MONOLIT = 5300
PORTA_GERBANG = 5310
PORTA_NASABAH = 5311
PORTA_PESANAN = 5312
PORTA_KURS = 5313

MONOLIT = f"{INDUK}:{PORTA_MONOLIT}"
GERBANG = f"{INDUK}:{PORTA_GERBANG}"
NASABAH = f"{INDUK}:{PORTA_NASABAH}"
PESANAN = f"{INDUK}:{PORTA_PESANAN}"
KURS = f"{INDUK}:{PORTA_KURS}"
