<?php
include 'config.php';

header('Content-Type: application/json');

// Check if it is a POST request
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(["error" => "Method not allowed. Use POST."]);
    exit;
}

// Read JSON data from the request body
$input = json_decode(file_get_contents('php://input'), true);

if (!isset($input['message_id']) || !isset($input['original_score']) || !isset($input['is_correct'])) {
    echo json_encode(["error" => "Required fields: message_id, original_score, is_correct"]);
    exit;
}

$message_id = intval($input['message_id']);
$original_score = intval($input['original_score']);
$is_correct = filter_var($input['is_correct'], FILTER_VALIDATE_BOOLEAN) ? 1 : 0;
$feedback_notes = isset($input['feedback_notes']) ? $input['feedback_notes'] : null;

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Connection failed: " . $conn->connect_error]);
    exit;
}

// Insert or update feedback
$sql = "
    INSERT INTO training_feedback 
    (message_id, original_score, is_correct, feedback_notes, reviewed_at)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON DUPLICATE KEY UPDATE
        is_correct = VALUES(is_correct),
        feedback_notes = VALUES(feedback_notes),
        reviewed_at = CURRENT_TIMESTAMP
";

$stmt = $conn->prepare($sql);
if (!$stmt) {
    echo json_encode(["error" => "Prepare failed: " . $conn->error]);
    $conn->close();
    exit;
}

$stmt->bind_param("iiis", $message_id, $original_score, $is_correct, $feedback_notes);

if (!$stmt->execute()) {
    echo json_encode(["error" => "Execute failed: " . $stmt->error]);
    $stmt->close();
    $conn->close();
    exit;
}

$stmt->close();
$conn->close();

echo json_encode([
    "success" => true,
    "message" => "Feedback saved successfully"
]);
?>
