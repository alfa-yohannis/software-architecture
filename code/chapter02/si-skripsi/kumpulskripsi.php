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

  $cek = mysqli_query($koneksi, "SELECT * FROM mhs_skripsi WHERE NIM='$nimquery'");
  $hasilcek = mysqli_num_rows($cek);
?>
<h3>Halaman Kumpul Skripsi</h3>
  <a href="mahasiswa.php">HOME</a> |
  <a href="kumpulproposal.php">KUMPUL PROPOSAL</a> |
  <a href="dataskripsi.php">DATABASE SKRIPSI</a> |
  <a href="kumpulskripsi.php">KUMPUL SKRIPSI</a>
  <hr>
  <a href="logout.php">LOG OUT</a>

	<hr>
<?php if($hasilcek > 0):?>
  <p>NOTICE : Anda sudah mengumpulkan skripsi </p>
<?php endif; ?>

<?php if($hasilcek == 0):?>
	<form method="POST" action="">
		<table>
			<tr>
				<td>Judul Skripsi</td>
				<td><input type="text" name="txtJudulSkripsi" size="45" maxlength="255" required></td>
			</tr>
      <tr>
				<td>Link BAB 1</td>
				<td><input type="text" name="txtBab1" size="45" required></td>
			</tr>
      <tr>
				<td>Link BAB 2</td>
				<td><input type="text" name="txtBab2" size="45" required></td>
			</tr>
      <tr>
				<td>Link BAB 3</td>
				<td><input type="text" name="txtBab3" size="45" required></td>
			</tr>
      <tr>
				<td>Link BAB 4</td>
				<td><input type="text" name="txtBab4" size="45" required></td>
			</tr>
      <tr>
				<td>Link BAB 5</td>
				<td><input type="text" name="txtBab5" size="45" required></td>
			</tr>
      <tr>
				<td>Link DAFTAR PUSTAKA</td>
				<td><input type="text" name="txtDaftarPustaka" size="45" required></td>
			</tr>
      <tr>
				<td>Link PAPER</td>
				<td><input type="text" name="txtPAPER" size="45" required></td>
			</tr>
			<tr>
				<td>Tahun Skripsi</td>
				<td><input type="number" name="txtTahunSkripsi" min="1900" max="2099" value="2021" size="11" required></td>
			</tr>
			<tr>
				<td></td>
				<td><input type="submit" name="add" value="add"></td>
			</tr>
	</table>
</form>

<p>ALERT : PASTIKAN DATA YANG ANDA SUDAH MASUKAN SUDAH BENAR</p>
<?php endif; ?>

<?php if(isset($_POST['add'])) :?>
<?php
include "koneksi.php";

if($_SERVER['REQUEST_METHOD']=='POST'){
	$add = mysqli_query($koneksi, "INSERT INTO skripsi(judul_skripsi,bab_1, bab_2, bab_3, bab_4, bab_5, daftar_pustaka, paper, tahun_skripsi)
	VALUE('$_POST[txtJudulSkripsi]','$_POST[txtBab1]','$_POST[txtBab2]','$_POST[txtBab3]','$_POST[txtBab4]','$_POST[txtBab5]','$_POST[txtDaftarPustaka]','$_POST[txtPAPER]','$_POST[txtTahunSkripsi]')");

	if($add){
    $jdsk = $_POST['txtJudulSkripsi'];
		$idskquery = mysqli_query($koneksi,"SELECT id_skripsi FROM skripsi WHERE judul_skripsi='$jdsk'");
    $hasilidsk = mysqli_fetch_array($idskquery);

    $add2 = mysqli_query($koneksi, "INSERT INTO mhs_skripsi(NIM, id_skripsi) VALUE('$_SESSION[nim]','$hasilidsk[id_skripsi]')");

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
