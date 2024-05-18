
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

DROP TABLE IF EXISTS `employee`;

CREATE TABLE `employee` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `age` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `employee` VALUES (1,'Lionel Messi','lionel.messi@intermiami.fc','35'),(2,'Luis Suarez','luis.suarez@intermiami.fc','36');
