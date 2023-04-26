const express = require("express");
const app = express();
const port = 3002;

// Endpoint untuk menampilkan data dosen
app.get("/dosen", (req, res) => {
  const dataDosen = [
    { nip: "201", nama: "Dewi", prodi: "Teknik Informatika" },
    { nip: "202", nama: "Eka", prodi: "Sistem Informasi" },
    { nip: "203", nama: "Fira", prodi: "Teknik Komputer" },
  ];

  res.send(dataDosen);
});

// Jalankan server
app.listen(port, () => {
  console.log(`Server Microservice 2 berjalan pada http://localhost:${port}`);
});
