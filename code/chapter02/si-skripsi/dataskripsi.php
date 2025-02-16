<?php
	session_start();
  error_reporting(E_ALL ^ E_NOTICE);
	if($_SESSION['level']==""){
    if($_SESSION['nim']==""){
  		header("location:loginmhs.php?pesan=belum");
  	}
	}
?>
<h1>Data Skripsi</h1>
<?php
 if(isset($_POST['search'])){
   $valueToSearch = $_POST['valueToSearch'];
   $query = "SELECT * FROM skripsi NATURAL LEFT JOIN grade NATURAL JOIN mhs_skripsi  NATURAL JOIN mahasiswa JOIN peminatan USING(peminatan_studi) WHERE (NIM LIKE '%$valueToSearch%') OR (nama_mahasiswa LIKE '%$valueToSearch%') OR (angkatan LIKE '%$valueToSearch%') OR (peminatan.prodi LIKE '%$valueToSearch%') OR (mahasiswa.peminatan_studi LIKE '%$valueToSearch%') OR (judul_skripsi LIKE '%$valueToSearch%')
	 OR (tahun_skripsi LIKE '%$valueToSearch%') ";
   $search_result = filterTable($query);
 }
 else{
   $query = "SELECT * FROM viewskripsi";
   $search_result = filterTable($query);
 }

 function filterTable($query){
   include "koneksi.php";
   $filter_result = mysqli_query($koneksi, $query);
   return $filter_result;
 }

 ?>
<?php error_reporting(E_ALL ^ E_NOTICE); if($_SESSION['username']):?>
	<a href="prodi.php">HOME</a> |
	<a href="datamhs.php">DATABASE MAHASISWA</a> |
	<a href="datadosen.php">DATABASE DOSEN</a> |
	<a href="dataproposal.php">CEK PROPOSAL</a> |
	<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
  <hr>
  <a href="logout.php">LOG OUT</a> <br> <br>
  <form action="dataskripsi.php" method="post">
  	<input type="text" name="valueToSearch" placeholder="Search">
  	<input type="submit" name="search" value="filter">
  	<a href="dataskripsi.php">RESET SEARCH</a>
  </form>

  <table border="1" cellspacing="0" align="center" width="90%">
  	<tr>
      <th>Judul Skripsi</th>
      <th>NIM</th>
  		<th>Nama Mahasiswa</th>
  		<th>Tahun Skripsi</th>
  		<th>Bab 1</th>
      <th>Bab 2</th>
      <th>Bab 3</th>
      <th>Bab 4</th>
      <th>Bab 5</th>
  		<th>Paper</th>
  		<th>Daftar Pustaka</th>
      <th>Nilai Skripsi</th>
      <th>Grade Skripsi</th>
      <th>Aksi</th>
  	</tr>
  	<?php while($row = mysqli_fetch_array($search_result)){
  		echo "<tr>
        <td>$row[judul_skripsi]</td>
  			<td>$row[NIM]</td>
  			<td>$row[nama_mahasiswa]</td>
  			<td>$row[tahun_skripsi]</td>
  			<td><a href='$row[bab_1]'>Link</a></td>
  			<td><a href='$row[bab_2]'>Link</a></td>
        <td><a href='$row[bab_3]'>Link</a></td>
        <td><a href='$row[bab_4]'>Link</a></td>
  			<td><a href='$row[bab_5]'>Link</a></td>
				<td><a href='$row[paper]'>Link</a></td>
				<td><a href='$row[daftar_pustaka]'>Link</a></td>
				<td>$row[nilai_skripsi]</td>
				<td>$row[grade_skripsi]</td>
  			<td><a href='nilaiskripsi.php?id_skripsi=$row[id_skripsi]'>Nilai Skripsi</a> | <a href='gagalskripsi.php?id_skripsi=$row[id_skripsi]'>Hapus/Gagalkan Skripsi</a>  </td></tr>";
  	}
  	?>
  </table>
<?php endif; ?>
<?php if($_SESSION['nim']):?>
  <a href="mahasiswa.php">HOME</a> |
  <a href="kumpulproposal.php">KUMPUL PROPOSAL</a> |
  <a href="dataskripsi.php">DATABASE SKRIPSI</a> |
  <a href="kumpulskripsi.php">KUMPUL SKRIPSI</a>
  <hr>
  <a href="logout.php">LOG OUT</a> <br> <br>
  <form action="dataskripsi.php" method="post">
  	<input type="text" name="valueToSearch" placeholder="Search">
  	<input type="submit" name="search" value="filter">
  	<a href="dataskripsi.php">RESET SEARCH</a>
  </form>

  <table border="1" cellspacing="0" align="center" width="90%">
  	<tr>
      <th>Judul Skripsi</th>
      <th>NIM</th>
  		<th>Nama Mahasiswa</th>
  		<th>Tahun Skripsi</th>
  		<th>Bab 1</th>
      <th>Bab 2</th>
      <th>Bab 5</th>
  		<th>Daftar Pustaka</th>
  	</tr>
  	<?php while($row = mysqli_fetch_array($search_result)){
  		echo "<tr>
        <td>$row[judul_skripsi]</td>
  			<td>$row[NIM]</td>
  			<td>$row[nama_mahasiswa]</td>
  			<td>$row[tahun_skripsi]</td>
  			<td><a href='$row[bab_1]'>Link</a></td>
  			<td><a href='$row[bab_2]'>Link </a></td>
  			<td><a href='$row[bab_5]'>Link</a></td>
				<td><a href='$row[daftar_pustaka]'>Link</a></td>
  			</tr>";
  	}
  	?>
  </table>
<?php endif; ?>
