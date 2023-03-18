const yup = require("yup");

const signupSchema = yup.object({
  nama: yup.string().required(),
  email: yup.string().required().email(),
  password: yup.string().required().min(6),
  admin: yup.boolean().required(),
});

const signinSchema = yup.object({
  email: yup.string().required().email(),
  password: yup.string().required().min(6),
});

module.exports = { signupSchema, signinSchema };
