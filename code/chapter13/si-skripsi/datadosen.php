<?php
	session_start();
	if($_SESSION['level']==""){
		header("location:login.php?pesan=belum");
	}

	if(isset($_POST['search'])){
		$valueToSearch = $_POST['valueToSearch'];
		$query = "SELECT * FROM dosen NATURAL JOIN `jumlah_mhs-dosen` WHERE (NIP LIKE '%$valueToSearch%') OR (NIK LIKE '%$valueToSearch%') OR (nama_dosen LIKE '%$valueToSearch%') OR (dosen.prodi LIKE '%$valueToSearch%') OR (kompetensi LIKE '%$valueToSearch%') OR (jml_mahasiswa LIKE '%$valueToSearch%') ";
		$search_result = filterTable($query);
	}
	else{
		$query = "SELECT dosen.NIP, NIK, nama_dosen, dosen.prodi, kompetensi, jml_mahasiswa, gelar FROM dosen NATURAL JOIN `jumlah_mhs-dosen` ";
		$search_result = filterTable($query);
	}

	function filterTable($query){
		include "koneksi.php";
		$filter_result = mysqli_query($koneksi, $query);
		return $filter_result;
	}

?>
<h1>Data Dosen</h1>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<hr>
<a href="logout.php">LOG OUT</a><br><br>
<form action="datadosen.php" method="post">
	<input type="text" name="valueToSearch" placeholder="Search">
	<input type="submit" name="search" value="filter">
	<a href="datadosen.php">RESET SEARCH</a>
</form>

<table border="1" cellspacing="0" align="center" width="90%">
	<tr>
    <th>NIP</th>
		<th>NIK</th>
		<th>Nama Dosen</th>
		<th>Program Studi</th>
    <th>Kompetensi</th>
		<th>Gelar</th>
		<th>Jumlah MHS dibimbing</th>
    <th>Aksi</th>
	</tr>
	<?php while($row = mysqli_fetch_array($search_result)){
		echo "<tr>
			<td>$row[NIP]</td>
      <td>$row[NIK]</td>
			<td>$row[nama_dosen]</td>
			<td>$row[prodi]</td>
			<td>$row[kompetensi]</td>
			<td>$row[gelar]</td>
			<td>$row[jml_mahasiswa]</td>
			<td><a href='editdosen.php?NIP=$row[NIP]'>Edit Data Dosen</a> | <a href='deletedosen.php?NIP=$row[NIP]'>Delete</a>  </td></tr>";
	}
	?>
</table>
<br>
<a href="adddosen.php">TAMBAH DOSEN</a>
