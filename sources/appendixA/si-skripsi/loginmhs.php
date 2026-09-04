<h3>Login Mahasiswa</h3>
<a href="login.php">Login Dashboard</a>
<a href="loginmhs.php">Login Mahasiswa</a>
<hr>
<form method="POST" action="cekloginmhs.php">
	<table>
		<tr>
			<td>NIM</td>
			<td><input type="text" name="nim" onkeypress="return /[0-9]/i.test(event.key)" maxlength="11" ></td>
		</tr>
		<tr>
			<td>Password</td>
			<td><input type="password" name="pass"></td>
		</tr>
		<tr>
			<td>Log In</td>
			<td><input type="submit" value="login" name="login"></td>
		</tr>
	</table>
</form>


<?php
	if(isset($_GET['pesan'])){
		if($_GET['pesan']=="gagal"){
			echo "Username dan Password tidak sesuai !";
		}
	}
  if(isset($_GET['pesan'])){
		if($_GET['pesan']=="belum"){
			echo "Belum Login !";
		}
	}
	?>
