<?php
include "koneksi.php";
$hapus = mysqli_query($koneksi, "DELETE FROM dosen WHERE NIP='$_GET[NIP]'");

if($hapus){
	header('location:datadosen.php');
}else{
	echo "Gagal menghapus data...";
}

 ?>
