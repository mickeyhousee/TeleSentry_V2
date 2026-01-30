<?php
include 'config.php';

header('Content-Type: application/json');

$limit = 5;
$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
$offset = ($page - 1) * $limit;
$query = isset($_GET['query']) ? '%' . $_GET['query'] . '%' : '%';

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}

// Prepare the main query
$sql = "
    SELECT 
        content.id_message, 
        content.date_message, 
        content.content, 
        content.translated_content, 
        COALESCE(user.name, user.username, 'Unknown') AS id_user, 
        `group`.group_name AS group_name
    FROM content
    JOIN user ON content.id_user = user.id_user
    JOIN `group` ON content.id_group = `group`.group_id
    WHERE content.content LIKE ? OR content.translated_content LIKE ?
    ORDER BY content.date_message DESC
    LIMIT ? OFFSET ?
";

$stmt = $conn->prepare($sql);
$stmt->bind_param("ssii", $query, $query, $limit, $offset);
$stmt->execute();
$result = $stmt->get_result();

if (!$result) {
    echo json_encode(["error" => $stmt->error]);
    exit;
}

$data = [];
while ($row = $result->fetch_assoc()) {
    $data[] = $row;
}

// Prepare the query to get the total number of messages
$countQuery = "
    SELECT COUNT(*) AS total 
    FROM content 
    WHERE content.content LIKE ? OR content.translated_content LIKE ?
";
$countStmt = $conn->prepare($countQuery);
$countStmt->bind_param("ss", $query, $query);
$countStmt->execute();
$countResult = $countStmt->get_result();
$totalMessages = $countResult->fetch_assoc()['total'];
$totalPages = ceil($totalMessages / $limit);

// Close statements and connection
$stmt->close();
$countStmt->close();
$conn->close();

echo json_encode([
    "messages" => $data,
    "totalPages" => $totalPages
]);
?>
