<?php
header('Content-Type: application/json');

$servername = "localhost";
$username = "grilo";
$password = "grilo";
$dbname = "search_telegram";

// Criar conexão
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar conexão
if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}

// Modificar a consulta SQL para obter os grupos e contagem de mensagens
$sql = "
    SELECT 
        `group`.group_id AS group_id, 
        `group`.group_name AS group_name, 
        (SELECT COUNT(*) FROM content WHERE content.id_group = `group`.group_id) AS message_count
    FROM 
        `group` 
    ORDER BY 
        `group`.group_id ASC
";

$result = $conn->query($sql);

if ($result === false) {
    die(json_encode(["error" => "Error: " . $conn->error]));
}

$groups = array();

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $groups[] = $row;
    }
}

$conn->close();

echo json_encode($groups);
?>
