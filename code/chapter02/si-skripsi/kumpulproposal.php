<?php
	session_start();
  error_reporting(E_ALL ^ E_NOTICE);
	if($_SESSION['level']==""){
    if($_SESSION['nim']==""){
  		header("location:loginmhs.php?pesan=belum");
  	}
	}
  include "koneksi.php";
  $nimquery = $_SESSION['nim'];

?>
<h3>Halaman Kumpul Proposal</h3>
  <a href="mahasiswa.php">HOME</a> |
  <a href="kumpulproposal.php">KUMPUL PROPOSAL</a> |
  <a href="dataskripsi.php">DATABASE SKRIPSI</a> |
  <a href="kumpulskripsi.php">KUMPUL SKRIPSI</a>
  <hr>
  <a href="logout.php">LOG OUT</a>

	<hr>

	<form method="POST" action="">
		<table>
			<tr>
				<td>Judul Topik</td>
				<td><input type="text" name="txtJudulTopik" size="45" maxlength="255" required></td>
			</tr>
      <tr>
				<td>Link File Proposal</td>
				<td><input type="text" name="txtFile" size="45" required></td>
			</tr>
			<tr>
				<td></td>
				<td><input type="submit" name="add" value="add"></td>
			</tr>
	</table>
</form>


<?php if(isset($_POST['add'])) :?>
<?php
include "koneksi.php";

if($_SERVER['REQUEST_METHOD']=='POST'){
	$add = mysqli_query($koneksi, "INSERT INTO proposal(judul_topik, file_proposal, status_proposal)
	VALUE('$_POST[txtJudulTopik]','$_POST[txtFile]','Menunggu')");

	if($add){
    $jdtpk = $_POST['txtJudulTopik'];
    $fltpk = $_POST['txtFile'];
		$idtpkquery = mysqli_query($koneksi,"SELECT id_topik FROM proposal WHERE judul_topik='$jdtpk' AND file_proposal='$fltpk' ");
    $hasil = mysqli_fetch_array($idtpkquery);

    $add2 = mysqli_query($koneksi, "INSERT INTO mhs_proposal(NIM, id_topik) VALUE('$_SESSION[nim]','$hasil[id_topik]')");

    if($add2){
      header("location:mahasiswa.php?pesan=berhasil");
    }else {
      echo "Gagal memasukkan data";
    }
	}else{
		echo "Gagal memasukkan data";
	}
}

?>
<?php endif; ?>
