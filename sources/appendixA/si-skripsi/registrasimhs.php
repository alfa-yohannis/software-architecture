<?php
	session_start();
	if($_SESSION['level']==""){
		header("location:login.php?pesan=belum");
	}
?>
<h3>Halaman Registasi Data diri Mahasiswa</h3>
<?php if($_SESSION['username']=='prodi'):?>
	<a href="prodi.php">HOME</a> |
	<a href="datamhs.php">DATABASE MAHASISWA</a> |
	<a href="datadosen.php">DATABASE DOSEN</a> |
	<a href="dataproposal.php">CEK PROPOSAL</a> |
	<a href="dataskripsi.php">DATABASE SKRIPSI</a> |
<?php endif; ?>

<a href="logout.php">LOG OUT</a>
<form method="POST" action="">
	<table>
		<tr>
			<td>Prodi</td>
			<td><select name="txtProdi">
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
				<td><input type="text" name="txtNIM" size="11" onkeypress="return /[0-9]/i.test(event.key)" maxlength="11" required ></td>
			</tr>
			<tr>
				<td>Nama Mahasiswa</td>
				<td><input type="text" name="txtNamaMhs" size="45" maxlength="255" required></td>
			</tr>
			<tr>
				<td>Angkatan</td>
				<td><input type="number" name="txtAngkatan" min="1900" max="2099" value="2020" size="11" required></td>
			</tr>
			<tr>
				<td>Peminatan studi</td>
				<td><select name="txtPeminatan">
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
				<td>Password</td>
				<td><input type="password" name="txtPassword" size="11" maxlength="11" required></td>
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
	$add = mysqli_query($koneksi, "INSERT INTO mahasiswa(NIM,nama_mahasiswa, angkatan, peminatan_studi, password_mhs)
	VALUE('$_POST[txtNIM]','$_POST[txtNamaMhs]','$_POST[txtAngkatan]','$_POST[txtPeminatan]','$_POST[txtPassword]')");

	if($add){
		header("location:registrasimhs.php?pesan=berhasil");
	}else{
		echo "Gagal memasukkan data";
	}
}

?>
<?php endif; ?>

<?php
	if(isset($_GET['pesan'])){
		if($_GET['pesan']=="berhasil"){
			echo "Berhasil menambah data";
			echo "<a href='logout.php'>Back</a>";
		}
	}
?>
