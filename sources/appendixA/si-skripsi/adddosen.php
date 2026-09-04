<h3>Add Dosen</h3>
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


		<hr>
		<form method="POST" action="">
			<table>
				<tr>
					<td>NIP</td>
					<td><input type="text" name="txtNIP" size="11" onkeypress="return /[0-9]/i.test(event.key)" maxlength="11" required ></td>
				</tr>
        <tr>
					<td>NIK</td>
					<td><input type="text" name="txtNIK" size="11" onkeypress="return /[0-9]/i.test(event.key)" maxlength="11" ></td>
				</tr>
				<tr>
					<td>Nama Dosen</td>
					<td><input type="text" name="txtNamaDosen" size="45" maxlength="255" required></td>
				</tr>
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
					<td>Kompetensi</td>
					<td><input type="text" name="txtKompetensi" size="45" maxlength="255" value=""></td>
				</tr>
				<tr>
					<td>Gelar</td>
					<td><input type="text" name="txtGelar" size="45" maxlength="255" value=""></td>
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
  	$add = mysqli_query($koneksi, "INSERT INTO dosen(NIP, NIK, nama_dosen, prodi, kompetensi, gelar)
  	VALUE('$_POST[txtNIP]','$_POST[txtNIK]','$_POST[txtNamaDosen]','$_POST[txtProdi]','$_POST[txtKompetensi]','$_POST[txtGelar]')");

  	if($add){
  		header("location:adddosen.php?pesan=berhasil");
  	}else{
  		echo "Gagal memasukkan data";
  	}
  }

  ?>
<?php endif; ?>

<?php
	if(isset($_GET['pesan'])){
		if($_GET['pesan']=="berhasil"){
			echo "Berhasil menambah data <br>";
			echo "<a href='datadosen.php'>Back</a>";
		}
	}
?>
