<?php
include 'config.php';

header('Content-Type: application/json');

$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
$limit = isset($_GET['limit']) ? intval($_GET['limit']) : 50;
$min_score = isset($_GET['min_score']) ? intval($_GET['min_score']) : 0;
$offset = ($page - 1) * $limit;

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Connection failed: " . $conn->connect_error]);
    exit;
}

// Query to get total count
$countSql = "
    SELECT COUNT(*) as total
    FROM message_scores ms
    INNER JOIN content c ON ms.message_id = c.id_message
    WHERE ms.score >= ?
";

$countStmt = $conn->prepare($countSql);
if (!$countStmt) {
    echo json_encode(["error" => "Prepare failed: " . $conn->error]);
    $conn->close();
    exit;
}

$countStmt->bind_param("i", $min_score);
$countStmt->execute();
$countResult = $countStmt->get_result();
$totalCount = $countResult->fetch_assoc()['total'];
$countStmt->close();

// Query to get scores with pagination
$sql = "
    SELECT 
        c.id_message,
        c.date_message,
        c.content,
        c.translated_content,
        u.username AS sender_username,
        u.name AS sender_name,
        g.group_name,
        ms.score,
        ms.sensitive_terms_count,
        ms.suspicious_links_count,
        ms.repeated_sharing,
        ms.high_risk_user,
        ms.calculated_at,
        tf.is_correct,
        tf.reviewed_at
    FROM message_scores ms
    INNER JOIN content c ON ms.message_id = c.id_message
    LEFT JOIN `user` u ON c.id_user = u.id_user
    LEFT JOIN `group` g ON c.id_group = g.group_id
    LEFT JOIN training_feedback tf ON ms.message_id = tf.message_id
    WHERE ms.score >= ?
    ORDER BY ms.score DESC, c.date_message DESC
    LIMIT ? OFFSET ?
";

$stmt = $conn->prepare($sql);
if (!$stmt) {
    echo json_encode(["error" => "Prepare failed: " . $conn->error]);
    $conn->close();
    exit;
}

$stmt->bind_param("iii", $min_score, $limit, $offset);
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

$totalPages = ceil($totalCount / $limit);

echo json_encode([
    "scores" => $data,
    "total" => intval($totalCount),
    "page" => $page,
    "limit" => $limit,
    "total_pages" => $totalPages
]);
?>

