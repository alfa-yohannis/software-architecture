const { signin, signup } = require("../controllers/auth.controller");
const { validation } = require("../middlewares/validation.middleware");
const { signinSchema, signupSchema } = require("../validation/user.validation");
const router = require("express").Router();

router.post("/signup", validation(signupSchema), signup);
router.post("/signin", validation(signinSchema), signin);

module.exports = router;
