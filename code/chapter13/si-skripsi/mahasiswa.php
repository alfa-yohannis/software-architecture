<?php
	session_start();
	if($_SESSION['nim']==""){
		header("location:loginmhs.php?pesan=belum");
	}
  include "koneksi.php";
  $nimquery = $_SESSION['nim'];
  $namamhsquery = mysqli_query($koneksi,"SELECT nama_mahasiswa FROM mahasiswa WHERE NIM='$nimquery'");
  $hasilnama = mysqli_fetch_array($namamhsquery);

?>

<h3>Halaman Dashboard Mahasiswa</h3>
<p>Halo <b><?php echo htmlentities($hasilnama['nama_mahasiswa'], ENT_QUOTES, 'UTF-8') ?></b></p>
<a href="mahasiswa.php">HOME</a> |
<a href="kumpulproposal.php">KUMPUL PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<a href="kumpulskripsi.php">KUMPUL SKRIPSI</a>
<hr>
<a href="logout.php">LOG OUT</a><br>

<?php
 if(isset($_POST['search'])){
   $valueToSearch = $_POST['valueToSearch'];
   $query = "SELECT * FROM proposal NATURAL JOIN mhs_proposal  NATURAL JOIN mahasiswa JOIN peminatan USING(peminatan_studi) WHERE ((NIM LIKE '%$valueToSearch%') OR (nama_mahasiswa LIKE '%$valueToSearch%') OR (angkatan LIKE '%$valueToSearch%') OR (peminatan.prodi LIKE '%$valueToSearch%') OR (judul_topik LIKE '%$valueToSearch%')) AND NIM='$nimquery' ";
   $search_result = filterTable($query);
 }
 else{
   $query = "SELECT * FROM viewproposal WHERE NIM='$nimquery'";
   $search_result = filterTable($query);
 }

 function filterTable($query){
   include "koneksi.php";
   $filter_result = mysqli_query($koneksi, $query);
   return $filter_result;
 }

 ?>

 <h3 align="center">Your Proposal</h3>

 <form action="mahasiswa.php" method="post" align="center">
 	<input type="text" name="valueToSearch" placeholder="Search">
 	<input type="submit" name="search" value="filter">
 	<a href="mahasiswa.php">RESET SEARCH</a>
 </form>

 <table border="1" cellspacing="0" align="center" width="90%">
 	<tr>
 		<th>Judul Topik</th>
 		<th>NIM</th>
 		<th>Nama Mahasiswa</th>
 		<th>File Proposal</th>
 		<th>Status Proposal</th>
 	</tr>

 	<?php while($row = mysqli_fetch_array($search_result)){
 		echo "<tr>
 			<td>$row[judul_topik]</td>
 			<td>$row[NIM]</td>
 			<td>$row[nama_mahasiswa]</td>
 			<td><a href='$row[file_proposal]'>Link</a></td>
 			<td>$row[status_proposal]</td>
 			</tr>";
 	}
 	?>
 </table>

<?php
	if(isset($_GET['pesan'])){
		if($_GET['pesan']=="berhasil"){
			echo "Berhasil menambah data";
		}
	}
?>
