const yup = require("yup");

const barangSchema = yup.object({
  nama: yup.string().required().max(50),
  type: yup.string().required().max(50),
  quantity: yup.number().required().positive(),
  satuan: yup.string().required(),
  catatan: yup.string(),
  supplier: yup.string().required(),
  tanggal_pengiriman: yup.date().required(),
});

module.exports = barangSchema;
