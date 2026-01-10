<?php
include 'config.php';

header('Content-Type: application/json');

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Connection failed: " . $conn->connect_error]);
    exit;
}

// Total scored messages
$sql = "SELECT COUNT(*) as total FROM message_scores WHERE score > 0";
$result = $conn->query($sql);
$total_scored = $result->fetch_assoc()['total'];

// Reviewed messages
$sql = "SELECT COUNT(*) as total FROM training_feedback WHERE is_correct IS NOT NULL";
$result = $conn->query($sql);
$total_reviewed = $result->fetch_assoc()['total'];

// Correct messages
$sql = "SELECT COUNT(*) as total FROM training_feedback WHERE is_correct = 1";
$result = $conn->query($sql);
$total_correct = $result->fetch_assoc()['total'];

// Incorrect messages
$sql = "SELECT COUNT(*) as total FROM training_feedback WHERE is_correct = 0";
$result = $conn->query($sql);
$total_incorrect = $result->fetch_assoc()['total'];

// Pending messages
$sql = "
    SELECT COUNT(*) as total 
    FROM message_scores ms
    LEFT JOIN training_feedback tf ON ms.message_id = tf.message_id
    WHERE ms.score > 0 AND (tf.id IS NULL OR tf.is_correct IS NULL)
";
$result = $conn->query($sql);
$total_pending = $result->fetch_assoc()['total'];

// Calculate accuracy
$accuracy = $total_reviewed > 0 ? round(($total_correct / $total_reviewed) * 100, 2) : 0;

$conn->close();

echo json_encode([
    "total_scored" => intval($total_scored),
    "total_reviewed" => intval($total_reviewed),
    "total_correct" => intval($total_correct),
    "total_incorrect" => intval($total_incorrect),
    "total_pending" => intval($total_pending),
    "accuracy" => $accuracy
]);
?>
