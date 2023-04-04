<?php
$koneksi = mysqli_connect("db","php_docker","password","si_skripsi");

// Check connection
if (mysqli_connect_errno()){
	echo "Koneksi database gagal : " . mysqli_connect_error();
}



?>
