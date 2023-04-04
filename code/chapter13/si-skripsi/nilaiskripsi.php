<?php
	session_start();
  error_reporting(E_ALL ^ E_NOTICE);
	if($_SESSION['level']==""){
  	header("location:loginmhs.php?pesan=belum");
	}
?>
<?php
include "koneksi.php";

	$edit = mysqli_query($koneksi, "SELECT * FROM skripsi NATURAL LEFT JOIN grade NATURAL JOIN mhs_skripsi  NATURAL JOIN mahasiswa JOIN peminatan USING(peminatan_studi) WHERE id_skripsi='$_GET[id_skripsi]' ");
	$e=mysqli_fetch_array($edit);

?>
<h1>NILAI Skripsi</h1>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<hr>
<a href="dataskripsi.php">BACK</a> |
<a href="logout.php">LOG OUT</a> <br> <br>

<form method="POST" action="">
  <table>
    <tr>
      <td>Judul Skripsi</td>
      <td><?php echo $e['judul_skripsi']?></td>
    </tr>
    <tr>
      <td>NIM / Nama Mahasiswa</td>
      <td><?php echo $e['NIM']?> / <?php echo $e['nama_mahasiswa']?></td>
    </tr>
    <tr>
      <td>Tahun Skripsi</td>
      <td><?php echo $e['tahun_skripsi']?></td>
    </tr>
    <tr>
      <td>BAB 1</td>
      <td><a href='<?php echo $e['bab_1']?>'>Link</a></td>
    </tr>
    <tr>
      <td>BAB 2</td>
      <td><a href='<?php echo $e['bab_2']?>'>Link</a></td>
    </tr>
    <tr>
      <td>BAB 3</td>
      <td><a href='<?php echo $e['bab_3']?>'>Link</a></td>
    </tr>
    <tr>
      <td>BAB 4</td>
      <td><a href='<?php echo $e['bab_4']?>'>Link</a></td>
    </tr>
    <tr>
      <td>BAB 5</td>
      <td><a href='<?php echo $e['bab_5']?>'>Link</a></td>
    </tr>
    <tr>
      <td>Daftar Pustaka</td>
      <td><a href='<?php echo $e['daftar_pustaka']?>'>Link</a></td>
    </tr>
    <tr>
      <td>Paper</td>
      <td><a href='<?php echo $e['paper']?>'>Link</a></td>
    </tr>
    <tr>
      <td>NILAI</td>
      <td><input type="number" name="txtNILAI" min="0" max="10" size="2" required ></td>
    </tr>
    <tr>
      <td></td>
      <td><input type="submit" name="add" value="nilai"></td>
    </tr>
  </table>
</form>

<?php if(isset($_POST['add'])) :?>
<?php
include "koneksi.php";
if($_SERVER['REQUEST_METHOD']=='POST'){
	$update = mysqli_query($koneksi,"UPDATE skripsi SET nilai_skripsi='$_POST[txtNILAI]' WHERE id_skripsi='$_GET[id_skripsi]'	");
	if($update){
		header ('location:dataskripsi.php');
	}else{
		echo "gagal";
	}
}

?>
<?php endif; ?>
