"use strict";
const { Model } = require("sequelize");
module.exports = (sequelize, DataTypes) => {
  class Barang extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      this.belongsTo(models.User, {
        foreignKey: {
          allowNull: false,
        },
        as: "User",
      });
    }
  }
  Barang.init(
    {
      nama: DataTypes.STRING,
      type: DataTypes.STRING,
      quantity: DataTypes.INTEGER,
      satuan: DataTypes.STRING,
      catatan: DataTypes.TEXT,
      supplier: DataTypes.STRING,
      tanggal_pengiriman: DataTypes.DATE,
    },
    {
      freezeTableName: true,
      sequelize,
      modelName: "Barang",
    }
  );
  return Barang;
};
