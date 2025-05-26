const express = require("express");
const app = express();
const db = require("./models");
require("dotenv").config();
const authRoutes = require("./routes/auth.route");
const barangRoutes = require("./routes/barang.route");
const swaggerDocumentation = require("./documentation/setup");

app.use(express.json());
const port = process.env.PORT || 3000;
db.sequelize.sync().then(() => {
  app.listen(port, () => console.log("Server is running"));
});
app.use(swaggerDocumentation);
app.use("/api/v1", barangRoutes);
app.use("/api/v1", authRoutes);
