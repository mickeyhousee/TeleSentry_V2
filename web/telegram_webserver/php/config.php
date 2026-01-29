<?php
$servername = "localhost";
$username = "grilo";
$password = "grilo";
$dbname = "search_telegram";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}
?>
