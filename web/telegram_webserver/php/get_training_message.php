<?php
include 'config.php';

header('Content-Type: application/json');

$exclude_reviewed = isset($_GET['exclude_reviewed']) ? filter_var($_GET['exclude_reviewed'], FILTER_VALIDATE_BOOLEAN) : true;

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Connection failed: " . $conn->connect_error]);
    exit;
}

// Query to search a random scored message
if ($exclude_reviewed) {
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
            ms.high_risk_user
        FROM content c
        INNER JOIN message_scores ms ON c.id_message = ms.message_id
        LEFT JOIN `user` u ON c.id_user = u.id_user
        LEFT JOIN `group` g ON c.id_group = g.group_id
        LEFT JOIN training_feedback tf ON c.id_message = tf.message_id
        WHERE ms.score > 0 
        AND (tf.id IS NULL OR tf.is_correct IS NULL)
        ORDER BY RAND()
        LIMIT 1
    ";
} else {
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
            ms.high_risk_user
        FROM content c
        INNER JOIN message_scores ms ON c.id_message = ms.message_id
        LEFT JOIN `user` u ON c.id_user = u.id_user
        LEFT JOIN `group` g ON c.id_group = g.group_id
        WHERE ms.score > 0
        ORDER BY RAND()
        LIMIT 1
    ";
}

$result = $conn->query($sql);

if (!$result) {
    echo json_encode(["error" => "Query failed: " . $conn->error]);
    $conn->close();
    exit;
}

if ($result->num_rows === 0) {
    echo json_encode(["message" => null, "error" => "Nenhuma mensagem encontrada"]);
    $conn->close();
    exit;
}

$message = $result->fetch_assoc();

// Search links associated with the message
$linkSql = "SELECT link FROM links WHERE message_id = ?";
$linkStmt = $conn->prepare($linkSql);
$linkStmt->bind_param("i", $message['id_message']);
$linkStmt->execute();
$linkResult = $linkStmt->get_result();
$links = [];
while ($linkRow = $linkResult->fetch_assoc()) {
    $links[] = $linkRow['link'];
}
$linkStmt->close();
$message['links'] = $links;

// Check if there is feedback
$feedbackSql = "SELECT is_correct, feedback_notes FROM training_feedback WHERE message_id = ?";
$feedbackStmt = $conn->prepare($feedbackSql);
$feedbackStmt->bind_param("i", $message['id_message']);
$feedbackStmt->execute();
$feedbackResult = $feedbackStmt->get_result();
$feedback = $feedbackResult->fetch_assoc();
$feedbackStmt->close();

if ($feedback) {
    $message['feedback'] = $feedback;
} else {
    $message['feedback'] = null;
}

$conn->close();

echo json_encode(["message" => $message]);
?>
