<?php
	session_start();
	if($_SESSION['level']==""){
  	header("location:loginmhs.php?pesan=belum");
	}
?>
<h1>Data Proposal</h1>
<?php
 if(isset($_POST['search'])){
   $valueToSearch = $_POST['valueToSearch'];
   $query = "SELECT * FROM proposal NATURAL JOIN mhs_proposal  NATURAL JOIN mahasiswa JOIN peminatan USING(peminatan_studi) WHERE (NIM LIKE '%$valueToSearch%') OR (nama_mahasiswa LIKE '%$valueToSearch%') OR (angkatan LIKE '%$valueToSearch%') OR (peminatan.prodi LIKE '%$valueToSearch%') OR (judul_topik LIKE '%$valueToSearch%') ";
   $search_result = filterTable($query);
 }
 else{
   $query = "SELECT * FROM viewproposal";
   $search_result = filterTable($query);
 }

 function filterTable($query){
   include "koneksi.php";
   $filter_result = mysqli_query($koneksi, $query);
   return $filter_result;
 }

 ?>
	<a href="prodi.php">HOME</a> |
	<a href="datamhs.php">DATABASE MAHASISWA</a> |
	<a href="datadosen.php">DATABASE DOSEN</a> |
	<a href="dataproposal.php">CEK PROPOSAL</a> |
	<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
  <hr>
  <a href="logout.php">LOG OUT</a> <br> <br>

  <form action="dataproposal.php" method="post">
  	<input type="text" name="valueToSearch" placeholder="Search">
  	<input type="submit" name="search" value="filter">
  	<a href="dataproposal.php">RESET SEARCH</a>
  </form>

  <table border="1" cellspacing="0" align="center" width="90%">
  	<tr>
      <th>Judul Topik</th>
      <th>NIM</th>
  		<th>Nama Mahasiswa</th>
  		<th>File Proposal</th>
  		<th>Status Proposal</th>
      <th>Aksi</th>
  	</tr>

  	<?php while($row = mysqli_fetch_array($search_result)){
  		echo "<tr>
        <td>$row[judul_topik]</td>
  			<td>$row[NIM]</td>
  			<td>$row[nama_mahasiswa]</td>
  			<td><a href='$row[file_proposal]'>Link</a></td>
				<td>$row[status_proposal]</td>
  			<td><a href='approveproposal.php?id_topik=$row[id_topik]'>Ganti Status</a> |  <a href='editmhs.php?NIM=$row[NIM]'>Assign Dosen</a> </td></tr>";
  	}
  	?>
  </table>
