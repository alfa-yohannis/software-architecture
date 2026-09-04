const swaggerUI = require("swagger-ui-express");
const router = require("express").Router();
const YAML = require("yamljs");

const swaggerJsDocs = YAML.load("./documentation/api.yaml");

router.use("/api-docs", swaggerUI.serve, swaggerUI.setup(swaggerJsDocs));
module.exports = router;
