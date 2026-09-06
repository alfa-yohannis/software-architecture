# Berkas Pendukung Modul

Satu direktori per bab, nomornya sejalan dengan `module/chapterNN.tex` dan
`slides/sessionNN/`. Penjelasan tiap berkas ada pada `README.md` di dalam
direktori babnya.

## Menyiapkan venv lokal

Skrip berikut membuat venv di `.venv` pada akar repositori, lalu memasang
seluruh kebutuhan pustaka. Dijalankan sekali saja, dari akar repositori:

```bash
bash sources/siapkan_venv.sh
source .venv/bin/activate
```

Penerjemah lain dapat dipilih lewat peubah lingkungan `PYTHON`:

```bash
PYTHON=python3.12 bash sources/siapkan_venv.sh
```

Bila skripnya tidak dipakai, langkahnya dapat dikerjakan secara manual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r sources/requirements.txt
```

Pada Windows, baris pengaktifannya menjadi `.venv\Scripts\activate`.

## Kebutuhan pustaka

| Bab | Kebutuhan |
| --- | --- |
| 1 sampai 4 | Pustaka standar Python saja, tanpa pemasangan tambahan |
| 3 | Tambahan modul `tkinter`, pada Debian dan Ubuntu ada di paket `python3-tk` |
| 13 | Flask dan requests, tercantum di `requirements.txt` |

Direktori `java/`, `go/`, dan `rust-example/` di dalam beberapa bab adalah
bahan pembanding lintas bahasa, sehingga tidak dipakai pada latihan dan tidak
membutuhkan venv.

Seluruh skrip dijalankan dari direktori babnya, bukan dari akar repositori,
sebab beberapa skrip membaca berkas basis data yang berada di sebelahnya.
