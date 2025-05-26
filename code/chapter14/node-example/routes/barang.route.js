const { validation } = require("../middlewares/validation.middleware");
const barangSchema = require("../validation/barang.validation");
const { getAllBarang, getBarang, postBarang, putBarang, deleteBarang } = require("../controllers/barang.controller");
const router = require("express").Router();
const { verifyTokenAndAuthorization, verifyTokenAndAdmin } = require("../middlewares/verifyToken.middleware");

router.get("/barang", verifyTokenAndAuthorization, getAllBarang);
router.get("/barang/:id", verifyTokenAndAuthorization, getBarang);
router.post("/barang", verifyTokenAndAdmin, validation(barangSchema), postBarang);
router.put("/barang/:id", verifyTokenAndAdmin, validation(barangSchema), putBarang);
router.delete("/barang/:id", verifyTokenAndAdmin, deleteBarang);

module.exports = router;
