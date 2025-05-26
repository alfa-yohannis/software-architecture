const { Barang, User } = require("../models");

async function getBarang(req, res) {
  try {
    const id = req.params.id;
    const findedBarang = await Barang.findOne({
      where: { id },
      attributes: { exclude: ["UserId"] },
      include: {
        model: User,
        as: "User",
        attributes: ["nama"],
      },
    });
    if (findedBarang) {
      res.status(200).json(findedBarang);
    } else {
      res.status(404).json({ msg: "Barang not found" });
    }
  } catch (err) {
    res.status(500).json(err);
  }
}

async function getAllBarang(req, res) {
  try {
    const allBarang = await Barang.findAll({
      attributes: { exclude: ["UserId"] },
      include: {
        model: User,
        as: "User",
        attributes: ["nama"],
      },
    });
    if (allBarang.length != 0) {
      res.status(200).json(allBarang);
    } else {
      res.status(200).json({ msg: "Barang is empty" });
    }
  } catch (err) {
    res.status(500).json({ err });
  }
}

async function postBarang(req, res) {
  try {
    const UserId = req.query.UserId;
    const timestamp = new Date();
    const { nama, type, quantity, satuan, catatan, supplier, tanggal_pengiriman } = req.body;
    const newBarang = await Barang.create({
      nama: nama,
      type: type,
      quantity: quantity,
      satuan: satuan,
      catatan: catatan,
      supplier: supplier,
      tanggal_pengiriman: tanggal_pengiriman,
      createdAt: timestamp,
      updatedAt: timestamp,
      UserId,
    });
    res.status(201).json(newBarang);
  } catch (err) {
    res.status(500).json(err);
  }
}

async function putBarang(req, res) {
  try {
    const UserId = req.query.UserId;
    const timestamp = new Date();
    const { nama, type, quantity, satuan, catatan, supplier, tanggal_pengiriman } = req.body;
    const updatedBarang = await Barang.update(
      {
        nama,
        type,
        quantity,
        satuan,
        catatan,
        supplier,
        tanggal_pengiriman,
        UserId,
        updatedAt: timestamp,
      },
      { where: { id: req.params.id }, returning: true }
    );
    console.log(updatedBarang);
    if (updatedBarang[0] == 1) {
      res.status(200).json(updatedBarang[1][0]);
    } else {
      res.status(404).json({ msg: "Barang not found" });
    }
  } catch (err) {
    res.status(500).json(err);
  }
}

async function deleteBarang(req, res) {
  try {
    const id = req.params.id;
    const barang = await Barang.destroy({ where: { id } });
    if (barang) {
      res.status(200).json({ msg: "Barang has been deleted" });
    } else {
      res.status(404).json({ msg: "Barang not found" });
    }
  } catch (err) {
    res.status(500).json(err);
  }
}

module.exports = { getAllBarang, getBarang, postBarang, putBarang, deleteBarang };
