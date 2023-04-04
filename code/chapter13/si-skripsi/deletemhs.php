<?php
include "koneksi.php";
$hapus = mysqli_query($koneksi, "DELETE FROM mahasiswa WHERE NIM='$_GET[NIM]'");

if($hapus){
	header('location:datamhs.php');
}else{
	echo "Gagal menghapus data...";
}

 ?>
