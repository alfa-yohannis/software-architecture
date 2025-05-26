const { genSalt, hash, compare } = require("bcrypt");
const { sign, decode } = require("jsonwebtoken");
require("dotenv").config();
const { User } = require("../models");

async function signup(req, res) {
  try {
    const { nama, email, password, admin } = req.body;
    const salt = await genSalt();
    const hashedPassword = await hash(password, salt);
    const user = await User.create({
      nama,
      email,
      password: hashedPassword,
      admin,
    });
    res.status(201).json({ user });
  } catch (err) {
    res.status(404).json({ err });
  }
}

async function signin(req, res) {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ where: { email } });
    if (user.length != 0) {
      const isPassword = await compare(password, user.password);
      if (isPassword) {
        const accessToken = sign(
          {
            id: user.dataValues.id,
            admin: user.dataValues.admin,
          },
          process.env.JWT_SEC,
          { expiresIn: "1h" }
        );
        res.status(200).json({ token: accessToken });
      } else {
        res.status(404).json({ msg: "Login failed" });
      }
    } else {
      res.status(404).json({ msg: "Login failed" });
    }
  } catch (err) {
    res.status(404).json({ err });
  }
}

module.exports = { signup, signin };
