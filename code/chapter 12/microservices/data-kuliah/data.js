const express = require("express");
const app = express();
const port = 3004;

// Endpoint untuk menampilkan data mata kuliah
app.get("/dataKuliah", (req, res) => {
  const dataKuliah = [
    {
      kode: "MK001",
      nama: "Pemrograman Web",
      sks: 4,
      mahasiswa: ["Agus", "cici"],
      dosen: ["Dewi"],
    },
    {
      kode: "MK002",
      nama: "Basis Data",
      sks: 3,
      mahasiswa: ["Budi"],
      dosen: ["Eka"],
    },
    {
      kode: "MK003",
      nama: "Pemrograman Mobile",
      sks: 3,
      mahasiswa: ["Agus", "Budi", "cici"],
      dosen: ["Fira"],
    },
  ];

  res.send(dataKuliah);
});

// Jalankan server
app.listen(port, () => {
  console.log(`Server Microservice 4 berjalan pada http://localhost:${port}`);
});
