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

// Modificar a consulta SQL para obter os bots, grupos e contagem de mensagens
$sql = "
    SELECT 
        bot.id AS bot_id, 
        bot.name AS bot_name, 
        (SELECT GROUP_CONCAT(DISTINCT `content`.id_group SEPARATOR ', ') 
         FROM content 
         WHERE content.id_bot = bot.id) AS group_ids,
        (SELECT GROUP_CONCAT(DISTINCT `group`.group_name SEPARATOR ', ') 
         FROM content 
         JOIN `group` ON content.id_group = `group`.group_id 
         WHERE content.id_bot = bot.id) AS groups,
        (SELECT COUNT(*) 
         FROM content 
         WHERE content.id_bot = bot.id) AS message_count
    FROM 
        bot 
    ORDER BY 
        bot.id ASC
";

$result = $conn->query($sql);

if ($result === false) {
    die(json_encode(["error" => "Error: " . $conn->error]));
}

$bots = array();

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $bots[] = $row;
    }
}

$conn->close();

echo json_encode($bots);
?>
