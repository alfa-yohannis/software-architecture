<?php
session_start();
include "koneksi.php";
//menangkap username dan password yg dikirim dari form login
	$username = $_POST['username'];
	$password = $_POST['password'];

//seleksi data user dengan data yg ada didatabase, lalu dihitung jumlah data yang ditemukan
  $login = mysqli_query($koneksi,"SELECT * FROM user WHERE username='$username' AND BINARY password='$password'");
	$cek = mysqli_num_rows($login);

//logika untuk pengecekkan adakah atau tidak username pass yg sesuai
	if($cek > 0){
    $data = mysqli_fetch_assoc($login);
    if($data['level']=="prodi"){
      $_SESSION['username'] = $username;
  		$_SESSION['level'] = "prodi";
		  header("location:prodi.php");
    }else if($data['level']=="mahasiswa"){
      $_SESSION['username'] = $username;
		  $_SESSION['level'] = "mahasiswa";
      header("location:registrasimhs.php");
    }else{
      header("location:login.php?pesan=gagal");
    }
	}else {
  header("location:login.php?pesan=gagal");
}
?>
