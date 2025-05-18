
--DROP DATABASE IF EXISTS demo;
CREATE DATABASE IF NOT EXISTS demo;
USE demo;

DROP TABLE IF EXISTS `performance`;

CREATE TABLE `performance` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) DEFAULT NULL,
  `rate` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
--  KEY `fk_performance_employee_idx` (`employee_id`),
--  CONSTRAINT `fk_performance_employee` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `performance` VALUES (1,1,8),(2,2,9);
