<?php
	session_start();
	if($_SESSION['level']==""){
		header("location:login.php?pesan=belum");
	}

	if(isset($_POST['search'])){
		$valueToSearch = $_POST['valueToSearch'];
		$query = "SELECT * FROM mahasiswa LEFT JOIN dosen ON dosen.nip=mahasiswa.nip LEFT JOIN peminatan ON mahasiswa.peminatan_studi=peminatan.peminatan_studi WHERE (NIM LIKE '%$valueToSearch%') OR (nama_mahasiswa LIKE '%$valueToSearch%') OR (angkatan LIKE '%$valueToSearch%') OR (peminatan.prodi LIKE '%$valueToSearch%') OR (mahasiswa.peminatan_studi LIKE '%$valueToSearch%') OR (nama_dosen LIKE '%$valueToSearch%') ";
		$search_result = filterTable($query);
	}
	else{
		$query = "SELECT * FROM mahasiswa LEFT JOIN dosen ON dosen.nip=mahasiswa.nip LEFT JOIN peminatan ON mahasiswa.peminatan_studi=peminatan.peminatan_studi";
		$search_result = filterTable($query);
	}

	function filterTable($query){
		include "koneksi.php";
		$filter_result = mysqli_query($koneksi, $query);
		return $filter_result;
	}

?>

<h1>Data Mahasiswa</h1>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<hr>
<a href="logout.php">LOG OUT</a><br><br>
<form action="datamhs.php" method="post">
	<input type="text" name="valueToSearch" placeholder="Search">
	<input type="submit" name="search" value="filter">
	<a href="datamhs.php">RESET SEARCH</a>
</form>

<table border="1" cellspacing="0" align="center" width="90%">
	<tr>
    <th>NIM</th>
		<th>Nama Mahasiswa</th>
		<th>Angkatan</th>
		<th>Program Studi</th>
		<th>Peminatan</th>
		<th>Dosen Pembimbing</th>
    <th>Aksi</th>
	</tr>
	<?php while($row = mysqli_fetch_array($search_result)){
		echo "<tr>
			<td>$row[NIM]</td>
			<td>$row[nama_mahasiswa]</td>
			<td>$row[angkatan]</td>
			<td>$row[prodi]</td>
			<td>$row[peminatan_studi]</td>
			<td>$row[nama_dosen]</td>
			<td><a href='editmhs.php?NIM=$row[NIM]'>Edit Data/Assign Dosen</a> | <a href='deletemhs.php?NIM=$row[NIM]'>Delete</a>  </td></tr>";
	}
	?>
</table>
<br>
<a href="registrasimhs.php">TAMBAH MAHASISWA</a>
