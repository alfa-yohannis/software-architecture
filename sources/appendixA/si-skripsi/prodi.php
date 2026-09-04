<?php
	session_start();
	if($_SESSION['level']==""){
		header("location:login.php?pesan=belum");
	}
  ?>

<h3>Halaman Dashboard Prodi</h3>
<p>Halo <b><?php echo $_SESSION['username']; ?></b> Anda telah login sebagai <b><?php echo $_SESSION['level']; ?></b>.</p>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<hr>
<a href="logout.php">LOG OUT</a>
