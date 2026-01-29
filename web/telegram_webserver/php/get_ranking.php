<?php
include 'config.php';

header('Content-Type: application/json');

$limit = isset($_GET['limit']) ? intval($_GET['limit']) : 50;
$min_score = isset($_GET['min_score']) ? intval($_GET['min_score']) : 1;

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Connection failed: " . $conn->connect_error]);
    exit;
}

// Query to get ranking of messages that deserve attention
$sql = "
    SELECT 
        c.id_message,
        c.date_message,
        c.content,
        c.translated_content,
        u.username AS sender_username,
        u.name AS sender_name,
        g.group_name,
        COALESCE(ms.score, 0) AS score,
        COALESCE(ms.sensitive_terms_count, 0) AS sensitive_terms_count,
        COALESCE(ms.suspicious_links_count, 0) AS suspicious_links_count,
        COALESCE(ms.repeated_sharing, 0) AS repeated_sharing,
        COALESCE(ms.high_risk_user, 0) AS high_risk_user
    FROM content c
    LEFT JOIN `user` u ON c.id_user = u.id_user
    LEFT JOIN `group` g ON c.id_group = g.group_id
    LEFT JOIN message_scores ms ON c.id_message = ms.message_id
    WHERE COALESCE(ms.score, 0) >= ?
    ORDER BY COALESCE(ms.score, 0) DESC, c.date_message DESC
    LIMIT ?
";

$stmt = $conn->prepare($sql);
if (!$stmt) {
    echo json_encode(["error" => "Prepare failed: " . $conn->error]);
    $conn->close();
    exit;
}

$stmt->bind_param("ii", $min_score, $limit);
if (!$stmt->execute()) {
    echo json_encode(["error" => "Execute failed: " . $stmt->error]);
    $stmt->close();
    $conn->close();
    exit;
}

$result = $stmt->get_result();

if (!$result) {
    echo json_encode(["error" => "Query failed: " . $stmt->error]);
    $stmt->close();
    $conn->close();
    exit;
}

$data = [];
while ($row = $result->fetch_assoc()) {
    // Search links associated with the message
    $linkSql = "SELECT link FROM links WHERE message_id = ?";
    $linkStmt = $conn->prepare($linkSql);
    $linkStmt->bind_param("i", $row['id_message']);
    $linkStmt->execute();
    $linkResult = $linkStmt->get_result();
    $links = [];
    while ($linkRow = $linkResult->fetch_assoc()) {
        $links[] = $linkRow['link'];
    }
    $linkStmt->close();
    $row['links'] = $links;
    
    $data[] = $row;
}

$stmt->close();
$conn->close();

echo json_encode([
    "messages" => $data,
    "total" => count($data)
]);
?>

