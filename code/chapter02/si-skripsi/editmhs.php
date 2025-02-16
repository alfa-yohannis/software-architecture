<?php
	session_start();
	if($_SESSION['level']==""){
		header("location:login.php?pesan=belum");
	}
?>
<h1>Edit Mahasiswa / Assign Dosen</h1>
<a href="prodi.php">HOME</a> |
<a href="datamhs.php">DATABASE MAHASISWA</a> |
<a href="datadosen.php">DATABASE DOSEN</a> |
<a href="dataproposal.php">CEK PROPOSAL</a> |
<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<hr>
<a href="datamhs.php">BACK</a> |
<a href="logout.php">LOG OUT</a> <br> <br>

<?php
include "koneksi.php";

	$edit = mysqli_query($koneksi, "SELECT * FROM mahasiswa LEFT JOIN dosen ON dosen.nip=mahasiswa.nip LEFT JOIN peminatan ON mahasiswa.peminatan_studi=peminatan.peminatan_studi WHERE NIM='$_GET[NIM]' ");
	$e=mysqli_fetch_array($edit);

	?>

	<form method="POST" action="">
		<table>
			<tr>
				<td>Prodi</td>
				<td><select name="txtProdi"><option value="<?php echo $e['prodi']?>"><?php echo $e['prodi']?></option>
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
				<td></td>
				<td><input type="submit" name="cek" value="Cek Prodi"></td>
			</tr>
		</table>
	</form>

	<?php if(isset($_POST['cek'])) :?>
		<hr>
		<form method="POST" action="">
			<table>
				<tr>
					<td>NIM</td>
					<td><input type="text" name="txtNIM" size="11" onkeypress="return /[0-9]/i.test(event.key)" value="<?php echo $e['NIM']?>" maxlength="11" required ></td>
				</tr>
				<tr>
					<td>Nama Mahasiswa</td>
					<td><input type="text" name="txtNamaMhs" size="45" maxlength="255" value="<?php echo $e['nama_mahasiswa']?>" required></td>
				</tr>
				<tr>
					<td>Angkatan</td>
					<td><input type="number" name="txtAngkatan" min="1900" max="2099" value="<?php echo $e['angkatan']?>" size="11" required></td>
				</tr>
				<tr>
					<td>Peminatan studi</td>
					<td><select name="txtPeminatan"><option value="<?php echo $e['peminatan_studi']?>"><?php echo $e['peminatan_studi']?></option>
								<?php
								include "koneksi.php";
								$prodis = $_POST['txtProdi'];

								$pilihMinat=mysqli_query($koneksi,"SELECT * FROM peminatan WHERE prodi='$prodis' ");
								while($minat=mysqli_fetch_assoc($pilihMinat)):;
								?>
								<option value="<?php echo $minat["peminatan_studi"];?>">
										<?php echo $minat["peminatan_studi"];
												?>
										</option>
								<?php
										endwhile;
								?>
						</select></td>
				</tr>
				<tr>
					<td>DOSEN Pembimbing</td>
					<td><select name="txtDOSEN"><option value="<?php echo $e['nama_dosen']?>" placeholder="Pilih Dosen"></option>
								<?php
								include "koneksi.php";
								$prodis = $_POST['txtProdi'];
								$pilihDosen=mysqli_query($koneksi,"SELECT * FROM dosen WHERE prodi='$prodis'");
								while($dosen=mysqli_fetch_assoc($pilihDosen)):;
								?>
								<option value="<?php echo $dosen["NIP"];?>">
										<?php echo $dosen["nama_dosen"];?> - <?php echo $dosen["kompetensi"];?>
										</option>
								<?php	endwhile;	?>
						</select></td>
				</tr>
				<tr>
					<td></td>
					<td><input type="submit" name="add" value="add"></td>
				</tr>
		</table>
	</form>
	<?php endif; ?>


<?php if(isset($_POST['add'])) :?>
<?php
include "koneksi.php";
if($_SERVER['REQUEST_METHOD']=='POST'){
	$update = mysqli_query($koneksi,"UPDATE mahasiswa SET NIM='$_POST[txtNIM]',
													nama_mahasiswa ='$_POST[txtNamaMhs]',
													angkatan ='$_POST[txtAngkatan]',
													peminatan_studi = '$_POST[txtPeminatan]',
													NIP = '$_POST[txtDOSEN]'
												WHERE NIM='$_GET[NIM]'

	");
	if($update){
		header ('location:datamhs.php');
	}else{
		echo "gagal";
	}
}

?>
<?php endif; ?>
