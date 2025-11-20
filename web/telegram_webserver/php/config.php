<?php
$servername = "localhost";
$username = "grilo";
$password = "grilo";
$dbname = "search_telegram";

// Cria a conexão
$conn = new mysqli($servername, $username, $password, $dbname);

// Verifica a conexão
if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}
?>
