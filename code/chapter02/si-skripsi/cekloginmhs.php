<?php
session_start();
include "koneksi.php";

	if(isset($_POST['login'])){
	$nim = $_POST['nim'];
	$password = $_POST['pass'];

	$data = mysqli_query($koneksi, "SELECT * FROM mahasiswa WHERE NIM='$nim' AND BINARY password_mhs='$password' ");
	$cek = mysqli_num_rows($data);

	if($cek > 0){
		$_SESSION['nim'] = $nim;
		header("location:mahasiswa.php");
	}else{
		header("location:loginmhs.php?pesan=gagal");
	};

	};
?>