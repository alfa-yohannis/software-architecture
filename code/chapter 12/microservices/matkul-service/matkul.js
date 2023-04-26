const express = require("express");
const app = express();
const port = 3003;

// Endpoint untuk menampilkan data mata kuliah
app.get("/matakuliah", (req, res) => {
  const dataMatakuliah = [
    {
      kode: "MK001",
      nama: "Pemrograman Web",
      sks: 4,
    },
    {
      kode: "MK002",
      nama: "Basis Data",
      sks: 3,
    },
    {
      kode: "MK003",
      nama: "Pemrograman Mobile",
      sks: 3,
    },
  ];

  res.send(dataMatakuliah);
});

// Jalankan server
app.listen(port, () => {
  console.log(`Server Microservice 3 berjalan pada http://localhost:${port}`);
});
