<?php
include "koneksi.php";
$hapus = mysqli_query($koneksi, "DELETE FROM skripsi WHERE id_skripsi='$_GET[id_skripsi]'");

if($hapus){
	header('location:dataskripsi.php');
}else{
	echo "Gagal menghapus skripsi...";
}

 ?>
