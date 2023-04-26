const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const axios = require("axios");

const app = express();
app.use(bodyParser.json());
app.use(cors());

// Microservice 1: Menampilkan data mahasiswa
app.get("/mahasiswa", async (req, res) => {
  try {
    const { data } = await axios.get("http://localhost:3001/mahasiswa");
    res.send(data);
  } catch (err) {
    console.log(err);
  }
});

// Microservice 2: Menampilkan data dosen
app.get("/dosen", async (req, res) => {
  try {
    const { data } = await axios.get("http://localhost:3002/dosen");
    res.send(data);
  } catch (err) {
    console.log(err);
  }
});

// Microservice 3: Menampilkan data mata kuliah
app.get("/matakuliah", async (req, res) => {
  try {
    const { data } = await axios.get("http://localhost:3003/matakuliah");
    res.send(data);
  } catch (err) {
    console.log(err);
  }
});

// Microservice 4: Menampilkan data- kuliah
app.get("/datakuliah", async (req, res) => {
  try {
    const { data } = await axios.get("http://localhost:3004/datakuliah");
    res.send(data);
  } catch (err) {
    console.log(err);
  }
});

app.listen(3000, () => {
  console.log("Microservices berjalan di port 3000...");
});
