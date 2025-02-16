-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 19, 2022 at 03:23 AM
-- Server version: 10.1.28-MariaDB
-- PHP Version: 5.6.32

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `si_skripsi`
--

-- --------------------------------------------------------

--
-- Table structure for table `dosen`
--

CREATE TABLE `dosen` (
  `NIP` int(11) NOT NULL,
  `NIK` int(11) DEFAULT NULL,
  `nama_dosen` varchar(45) DEFAULT NULL,
  `prodi` varchar(45) DEFAULT NULL,
  `kompetensi` varchar(255) DEFAULT NULL,
  `gelar` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `dosen`
--

INSERT INTO `dosen` (`NIP`, `NIK`, `nama_dosen`, `prodi`, `kompetensi`, `gelar`) VALUES
(10000001, 20000001, 'THERESIA HERLINA', 'TEKNIK INFORMATIKA', 'UI/UX, Database. Programming', 'S.Kom., M.T'),
(10000002, 20000002, 'HARYONO', 'TEKNIK INFORMATIKA', 'IoT', 'S.Kom., M.Tech'),
(10000003, 20000003, 'ASEP', 'SISTEM INFORMASI', '', 'S.Pd., M.Ak.'),
(10000004, 20000004, 'HANDOKO', 'SISTEM INFORMASI', '', 'S.Pd., M.Ds.'),
(10000005, 20000005, 'CARLA', 'SISTEM INFORMASI', '', 'S.Pd., M.Ds.'),
(10000006, 20000006, 'ALIM', 'DESAIN KOMUNIKASI VISUAL', '', 'S.Pd., M.Ds.'),
(10000007, 20000007, 'SILVI', 'DESAIN KOMUNIKASI VISUAL', '', 'S.Pd., M.Si.'),
(10000008, 20000008, 'FADIL', 'DESAIN KOMUNIKASI VISUAL', '', 'S.Pd., M.Si.'),
(10000009, 20000009, 'BERNARD', 'AKUNTANSI', '', 'S.Pd., M.Si.'),
(10000010, 20000010, 'DIMAS', 'AKUNTANSI', '', 'S.Pd., M.Ak');

-- --------------------------------------------------------

--
-- Table structure for table `grade`
--

CREATE TABLE `grade` (
  `nilai_skripsi` int(11) NOT NULL,
  `grade_skripsi` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `grade`
--

INSERT INTO `grade` (`nilai_skripsi`, `grade_skripsi`) VALUES
(0, 'E'),
(1, 'E'),
(2, 'E'),
(3, 'E'),
(4, 'E'),
(5, 'D'),
(6, 'C'),
(7, 'C+'),
(8, 'B'),
(9, 'A'),
(10, 'A+');

-- --------------------------------------------------------

--
-- Stand-in structure for view `jumlah_mhs-dosen`
-- (See below for the actual view)
--
CREATE TABLE `jumlah_mhs-dosen` (
`NIP` int(11)
,`jml_mahasiswa` bigint(21)
);

-- --------------------------------------------------------

--
-- Table structure for table `mahasiswa`
--

CREATE TABLE `mahasiswa` (
  `NIM` int(10) NOT NULL,
  `NIP` int(11) DEFAULT NULL,
  `nama_mahasiswa` varchar(255) DEFAULT NULL,
  `angkatan` int(4) DEFAULT NULL,
  `peminatan_studi` varchar(255) DEFAULT NULL,
  `password_mhs` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `mahasiswa`
--

INSERT INTO `mahasiswa` (`NIM`, `NIP`, `nama_mahasiswa`, `angkatan`, `peminatan_studi`, `password_mhs`) VALUES
(1710101001, 10000001, 'RENALDO', 2017, 'UI/UX', 'mahasiswa'),
(2020202042, 10000001, 'ALBERT EINFEIN', 2020, 'CYBER SECURITY', 'mahasiswa'),
(2110101012, 10000002, 'DELVIN', 2021, 'UI/UX', 'mahasiswa'),
(2110101021, 10000002, 'RICHWEN CANADY', 2021, 'UI/UX', 'mahasiswa'),
(2110101025, 10000005, 'TOMMY CHITIAWAN', 2021, 'BUSINESS INTELLIGENCE', 'mahasiswa'),
(2120202020, 10000010, 'DEVI', 2021, 'TAXATION', 'mahasiswa'),
(2120202021, 10000010, 'MINA', 2021, 'AUDITING', 'mahasiswa'),
(2130303030, 10000004, 'TONI', 2021, 'BUSINESS INTELLIGENCE', 'mahasiswa'),
(2130303031, 10000004, 'THEO', 2021, 'INFORMATION SYSTEM GOVERNANCE', 'mahasiswa'),
(2130303032, 10000004, 'HANS', 2021, 'INFORMATION SYSTEM GOVERNANCE', 'mahasiswa'),
(2140404040, 10000006, 'RENALDY', 2021, 'DIGITAL AND INTERACTIVE MEDIA', 'mahasiswa'),
(2140404041, 10000007, 'DARRELL', 2021, 'VISUAL COMMUNICATION DESIGN FOR RETAIL', 'mahasiswa'),
(2140404042, 10000008, 'HAYKAL', 2021, 'VISUAL COMMUNICATION DESIGN FOR RETAIL', 'mahasiswa');

-- --------------------------------------------------------

--
-- Table structure for table `mhs_proposal`
--

CREATE TABLE `mhs_proposal` (
  `NIM` int(10) DEFAULT NULL,
  `id_topik` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `mhs_proposal`
--

INSERT INTO `mhs_proposal` (`NIM`, `id_topik`) VALUES
(2020202042, 8001),
(2110101012, 8002),
(2110101021, 8004);

-- --------------------------------------------------------

--
-- Table structure for table `mhs_skripsi`
--

CREATE TABLE `mhs_skripsi` (
  `NIM` int(10) NOT NULL,
  `id_skripsi` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `mhs_skripsi`
--

INSERT INTO `mhs_skripsi` (`NIM`, `id_skripsi`) VALUES
(1710101001, 9001),
(2020202042, 9002);

-- --------------------------------------------------------

--
-- Table structure for table `peminatan`
--

CREATE TABLE `peminatan` (
  `peminatan_studi` varchar(255) NOT NULL,
  `prodi` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `peminatan`
--

INSERT INTO `peminatan` (`peminatan_studi`, `prodi`) VALUES
('ARTIFICIAL INTELLIGENCE', 'TEKNIK INFORMATIKA'),
('AUDITING', 'AKUNTANSI'),
('BUSINESS INTELLIGENCE', 'SISTEM INFORMASI'),
('CYBER SECURITY', 'TEKNIK INFORMATIKA'),
('DIGITAL AND INTERACTIVE MEDIA', 'DESAIN KOMUNIKASI VISUAL'),
('ENTERPRISE SYSTEM', 'SISTEM INFORMASI'),
('INFORMATION SYSTEM GOVERNANCE', 'SISTEM INFORMASI'),
('TAXATION', 'AKUNTANSI'),
('UI/UX', 'TEKNIK INFORMATIKA'),
('VISUAL COMMUNICATION DESIGN FOR RETAIL', 'DESAIN KOMUNIKASI VISUAL');

-- --------------------------------------------------------

--
-- Table structure for table `proposal`
--

CREATE TABLE `proposal` (
  `id_topik` int(11) NOT NULL,
  `judul_topik` varchar(45) DEFAULT NULL,
  `file_proposal` varchar(1000) DEFAULT NULL,
  `status_proposal` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `proposal`
--

INSERT INTO `proposal` (`id_topik`, `judul_topik`, `file_proposal`, `status_proposal`) VALUES
(8001, 'Project Akhir IOT', NULL, 'Menunggu'),
(8002, 'Project Akhir IOT', NULL, 'Menunggu'),
(8004, 'Judul Topik 2', 'https://www.example.org', 'Menunggu');

-- --------------------------------------------------------

--
-- Table structure for table `skripsi`
--

CREATE TABLE `skripsi` (
  `id_skripsi` int(11) NOT NULL,
  `judul_skripsi` varchar(255) DEFAULT NULL,
  `nilai_skripsi` int(11) DEFAULT NULL,
  `bab_1` varchar(255) DEFAULT NULL,
  `bab_2` varchar(255) DEFAULT NULL,
  `bab_3` varchar(255) DEFAULT NULL,
  `bab_4` varchar(255) DEFAULT NULL,
  `bab_5` varchar(255) DEFAULT NULL,
  `paper` varchar(255) DEFAULT NULL,
  `daftar_pustaka` varchar(255) DEFAULT NULL,
  `tahun_skripsi` int(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `skripsi`
--

INSERT INTO `skripsi` (`id_skripsi`, `judul_skripsi`, `nilai_skripsi`, `bab_1`, `bab_2`, `bab_3`, `bab_4`, `bab_5`, `paper`, `daftar_pustaka`, `tahun_skripsi`) VALUES
(9001, 'Penggunaan Live2d di UI/UX', 10, 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 2021),
(9002, 'Judul Skripsi A', 10, 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 'https://www.example.org', 2021);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `level` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id_user`, `username`, `password`, `level`) VALUES
(1, 'prodi', 'prodi', 'prodi'),
(2, 'mahasiswa', 'mahasiswa', 'mahasiswa');

-- --------------------------------------------------------

--
-- Stand-in structure for view `viewproposal`
-- (See below for the actual view)
--
CREATE TABLE `viewproposal` (
`peminatan_studi` varchar(255)
,`NIM` int(10)
,`id_topik` int(11)
,`judul_topik` varchar(45)
,`file_proposal` varchar(1000)
,`status_proposal` varchar(45)
,`NIP` int(11)
,`nama_mahasiswa` varchar(255)
,`angkatan` int(4)
,`password_mhs` varchar(45)
,`prodi` varchar(45)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `viewskripsi`
-- (See below for the actual view)
--
CREATE TABLE `viewskripsi` (
`peminatan_studi` varchar(255)
,`NIM` int(10)
,`id_skripsi` int(11)
,`nilai_skripsi` int(11)
,`judul_skripsi` varchar(255)
,`bab_1` varchar(255)
,`bab_2` varchar(255)
,`bab_3` varchar(255)
,`bab_4` varchar(255)
,`bab_5` varchar(255)
,`paper` varchar(255)
,`daftar_pustaka` varchar(255)
,`tahun_skripsi` int(4)
,`grade_skripsi` varchar(2)
,`NIP` int(11)
,`nama_mahasiswa` varchar(255)
,`angkatan` int(4)
,`password_mhs` varchar(45)
,`prodi` varchar(45)
);

-- --------------------------------------------------------

--
-- Structure for view `jumlah_mhs-dosen`
--
DROP TABLE IF EXISTS `jumlah_mhs-dosen`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `jumlah_mhs-dosen`  AS  select `dosen`.`NIP` AS `NIP`,count(distinct `mahasiswa`.`NIM`) AS `jml_mahasiswa` from (`dosen` left join `mahasiswa` on((`dosen`.`NIP` = `mahasiswa`.`NIP`))) group by `dosen`.`NIP` ;

-- --------------------------------------------------------

--
-- Structure for view `viewproposal`
--
DROP TABLE IF EXISTS `viewproposal`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `viewproposal`  AS  select `mahasiswa`.`peminatan_studi` AS `peminatan_studi`,`mhs_proposal`.`NIM` AS `NIM`,`proposal`.`id_topik` AS `id_topik`,`proposal`.`judul_topik` AS `judul_topik`,`proposal`.`file_proposal` AS `file_proposal`,`proposal`.`status_proposal` AS `status_proposal`,`mahasiswa`.`NIP` AS `NIP`,`mahasiswa`.`nama_mahasiswa` AS `nama_mahasiswa`,`mahasiswa`.`angkatan` AS `angkatan`,`mahasiswa`.`password_mhs` AS `password_mhs`,`peminatan`.`prodi` AS `prodi` from (((`proposal` join `mhs_proposal` on((`proposal`.`id_topik` = `mhs_proposal`.`id_topik`))) join `mahasiswa` on((`mhs_proposal`.`NIM` = `mahasiswa`.`NIM`))) join `peminatan` on((`mahasiswa`.`peminatan_studi` = `peminatan`.`peminatan_studi`))) ;

-- --------------------------------------------------------

--
-- Structure for view `viewskripsi`
--
DROP TABLE IF EXISTS `viewskripsi`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `viewskripsi`  AS  select `mahasiswa`.`peminatan_studi` AS `peminatan_studi`,`mhs_skripsi`.`NIM` AS `NIM`,`skripsi`.`id_skripsi` AS `id_skripsi`,`skripsi`.`nilai_skripsi` AS `nilai_skripsi`,`skripsi`.`judul_skripsi` AS `judul_skripsi`,`skripsi`.`bab_1` AS `bab_1`,`skripsi`.`bab_2` AS `bab_2`,`skripsi`.`bab_3` AS `bab_3`,`skripsi`.`bab_4` AS `bab_4`,`skripsi`.`bab_5` AS `bab_5`,`skripsi`.`paper` AS `paper`,`skripsi`.`daftar_pustaka` AS `daftar_pustaka`,`skripsi`.`tahun_skripsi` AS `tahun_skripsi`,`grade`.`grade_skripsi` AS `grade_skripsi`,`mahasiswa`.`NIP` AS `NIP`,`mahasiswa`.`nama_mahasiswa` AS `nama_mahasiswa`,`mahasiswa`.`angkatan` AS `angkatan`,`mahasiswa`.`password_mhs` AS `password_mhs`,`peminatan`.`prodi` AS `prodi` from ((((`skripsi` left join `grade` on((`skripsi`.`nilai_skripsi` = `grade`.`nilai_skripsi`))) join `mhs_skripsi` on((`skripsi`.`id_skripsi` = `mhs_skripsi`.`id_skripsi`))) join `mahasiswa` on((`mhs_skripsi`.`NIM` = `mahasiswa`.`NIM`))) join `peminatan` on((`mahasiswa`.`peminatan_studi` = `peminatan`.`peminatan_studi`))) ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dosen`
--
ALTER TABLE `dosen`
  ADD PRIMARY KEY (`NIP`);

--
-- Indexes for table `grade`
--
ALTER TABLE `grade`
  ADD PRIMARY KEY (`nilai_skripsi`);

--
-- Indexes for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD PRIMARY KEY (`NIM`),
  ADD KEY `NIP` (`NIP`),
  ADD KEY `peminatan_studi` (`peminatan_studi`);

--
-- Indexes for table `mhs_proposal`
--
ALTER TABLE `mhs_proposal`
  ADD UNIQUE KEY `id_mhs_proposal` (`NIM`),
  ADD KEY `NIM` (`NIM`),
  ADD KEY `id_topik` (`id_topik`);

--
-- Indexes for table `mhs_skripsi`
--
ALTER TABLE `mhs_skripsi`
  ADD UNIQUE KEY `indexmhs-skripsi` (`NIM`),
  ADD KEY `id_skripsi` (`id_skripsi`);

--
-- Indexes for table `peminatan`
--
ALTER TABLE `peminatan`
  ADD PRIMARY KEY (`peminatan_studi`);

--
-- Indexes for table `proposal`
--
ALTER TABLE `proposal`
  ADD PRIMARY KEY (`id_topik`);

--
-- Indexes for table `skripsi`
--
ALTER TABLE `skripsi`
  ADD PRIMARY KEY (`id_skripsi`),
  ADD KEY `nilai_skripsi` (`nilai_skripsi`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `proposal`
--
ALTER TABLE `proposal`
  MODIFY `id_topik` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8005;

--
-- AUTO_INCREMENT for table `skripsi`
--
ALTER TABLE `skripsi`
  MODIFY `id_skripsi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9003;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD CONSTRAINT `mahasiswa_ibfk_1` FOREIGN KEY (`NIP`) REFERENCES `dosen` (`NIP`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `mahasiswa_ibfk_2` FOREIGN KEY (`peminatan_studi`) REFERENCES `peminatan` (`peminatan_studi`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `mhs_proposal`
--
ALTER TABLE `mhs_proposal`
  ADD CONSTRAINT `mhs_proposal_ibfk_1` FOREIGN KEY (`NIM`) REFERENCES `mahasiswa` (`NIM`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `mhs_proposal_ibfk_2` FOREIGN KEY (`id_topik`) REFERENCES `proposal` (`id_topik`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `mhs_skripsi`
--
ALTER TABLE `mhs_skripsi`
  ADD CONSTRAINT `mhs_skripsi_ibfk_1` FOREIGN KEY (`id_skripsi`) REFERENCES `skripsi` (`id_skripsi`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `mhs_skripsi_ibfk_2` FOREIGN KEY (`NIM`) REFERENCES `mahasiswa` (`NIM`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `skripsi`
--
ALTER TABLE `skripsi`
  ADD CONSTRAINT `skripsi_ibfk_1` FOREIGN KEY (`nilai_skripsi`) REFERENCES `grade` (`nilai_skripsi`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
