<h3>Edit Dosen</h3>
<?php
	session_start();
	if($_SESSION['level']==""){
		header("location:login.php?pesan=belum");
	}
?>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a>
<hr>
<a href="datadosen.php">BACK</a>
<a href="logout.php">LOG OUT</a>
<?php
include "koneksi.php";
	$edit = mysqli_query($koneksi, "SELECT * FROM dosen WHERE NIP='$_GET[NIP]' ");
	$e=mysqli_fetch_array($edit);
?>

		<hr>
		<form method="POST" action="">
			<table>
				<tr>
					<td>NIP</td>
					<td><input type="text" name="txtNIP" size="11" onkeypress="return /[0-9]/i.test(event.key)" value="<?php echo $e['NIP']?>" maxlength="11" required ></td>
				</tr>
        <tr>
					<td>NIK</td>
					<td><input type="text" name="txtNIK" size="11" onkeypress="return /[0-9]/i.test(event.key)" value="<?php echo $e['NIK']?>" maxlength="11" required ></td>
				</tr>
				<tr>
					<td>Nama Dosen</td>
					<td><input type="text" name="txtNamaDosen" size="45" maxlength="255" value="<?php echo $e['nama_dosen']?>" required></td>
				</tr>
        <tr>
  				<td>Prodi</td>
  				<td><select name="txtProdi"> <option value="<?php echo $e['prodi']?>"><?php echo $e['prodi']?></option>
  	            <?php
  	            include "koneksi.php";
  	            $pilihProdi=mysqli_query($koneksi,"SELECT DISTINCT prodi FROM peminatan");
  	            while($prodi=mysqli_fetch_assoc($pilihProdi)):;
  	            ?>
  	            <option value="<?php echo $prodi["prodi"];?>">
  	                <?php echo $prodi["prodi"];
  	                        // To show the category name to the user
  	                  ?>
  	                </option>
  	            <?php
  	                endwhile;
  	            ?>
  	        </select>
  	      </td>
  			</tr>
				<tr>
					<td>Kompetensi</td>
					<td><input type="text" name="txtKompetensi" size="45" maxlength="255" value="<?php echo $e['kompetensi']?>"></td>
				</tr>
				<tr>
					<td>Gelar</td>
					<td><input type="text" name="txtGelar" size="45" maxlength="255" value="<?php echo $e['gelar']?>"></td>
				</tr>
				<tr>
					<td></td>
					<td><input type="submit" name="add" value="edit"></td>
				</tr>
		</table>
	</form>



<?php if(isset($_POST['add'])) :?>
<?php
include "koneksi.php";
if($_SERVER['REQUEST_METHOD']=='POST'){
	$update = mysqli_query($koneksi,"UPDATE dosen SET NIP='$_POST[txtNIP]',
                          NIK='$_POST[txtNIK]',
													nama_dosen ='$_POST[txtNamaDosen]',
													prodi ='$_POST[txtProdi]',
                          kompetensi = '$_POST[txtKompetensi]',
													gelar = '$_POST[txtGelar]'
												WHERE dosen.NIP='$_GET[NIP]'");
	if($update){
		header ('location:datadosen.php');
	}else{
		echo "gagal";
	}
}

?>
<?php endif; ?>
