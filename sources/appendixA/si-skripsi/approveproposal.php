<?php
	session_start();
  error_reporting(E_ALL ^ E_NOTICE);
	if($_SESSION['level']==""){
  	header("location:loginmhs.php?pesan=belum");
	}
?>
<?php
include "koneksi.php";

	$edit = mysqli_query($koneksi, "SELECT * FROM proposal NATURAL JOIN mhs_proposal NATURAL JOIN mahasiswa JOIN peminatan USING(peminatan_studi) WHERE id_topik='$_GET[id_topik]' ");
	$e=mysqli_fetch_array($edit);

?>
<h1>Ganti Status Proposal</h1>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<hr>
<a href="dataproposal.php">BACK</a> |
<a href="logout.php">LOG OUT</a> <br> <br>

<form method="POST" action="">
  <table>
    <tr>
      <td>Judul Topik</td>
      <td><?php echo $e['judul_topik']?></td>
    </tr>
    <tr>
      <td>NIM / Nama Mahasiswa</td>
      <td><?php echo $e['NIM']?> / <?php echo $e['nama_mahasiswa']?></td>
    </tr>
    <tr>
      <td>File Proposal</td>
      <td><a href='<?php echo $e['file_proposal']?>'>Link</a></td>
    </tr>
    <tr>
      <td>Status Proposal</td>
      <td> <select name="txtStatus">
        <option value="Menunggu">Menunggu</option>
        <option value="Approved with Revision">Approved with Revision</option>
        <option value="Approved without Revision">Approved without Revision</option>
        <option value="Di tolak">Di tolak</option>
      </select> </td>
    </tr>
    <tr>
      <td></td>
      <td><input type="submit" name="add" value="Ganti"></td>
    </tr>
  </table>
</form>

<?php if(isset($_POST['add'])) :?>
<?php
include "koneksi.php";
if($_SERVER['REQUEST_METHOD']=='POST'){
	$update = mysqli_query($koneksi,"UPDATE proposal SET status_proposal='$_POST[txtStatus]' WHERE id_topik='$_GET[id_topik]'	");
	if($update){
		header ('location:dataproposal.php');
	}else{
		echo "gagal";
	}
}

?>
<?php endif; ?>
