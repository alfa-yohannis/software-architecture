const express = require("express");
const app = express();
const port = 3001;

// Endpoint untuk menampilkan data mahasiswa
app.get("/mahasiswa", (req, res) => {
  const dataMahasiswa = [
    { nim: "101", nama: "Agus", jurusan: "Teknik Informatika" },
    { nim: "102", nama: "Budi", jurusan: "Sistem Informasi" },
    { nim: "103", nama: "Cici", jurusan: "Teknik Komputer" },
  ];

  res.send(dataMahasiswa);
});

// Jalankan server
app.listen(port, () => {
  console.log(`Server Microservice 1 berjalan pada http://localhost:${port}`);
});
