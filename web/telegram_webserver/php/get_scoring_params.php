<?php
include 'config.php';

header('Content-Type: application/json');

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    echo json_encode(["error" => "Connection failed: " . $conn->connect_error]);
    exit;
}

// Default weights
$default_weights = [
    "sensitive_terms" => 3.0,
    "suspicious_links" => 4.0,
    "repeated_sharing" => 2.0,
    "high_risk_user" => 5.0
];

// Calculate adjusted weights based on training feedback
// Strategy: If many messages with a specific factor were marked as incorrect,
// we reduce the weight of that factor. If marked as correct, we maintain or increase.

$adjusted_weights = $default_weights;

// Get training feedback with message details
$query = "
    SELECT 
        tf.is_correct,
        ms.sensitive_terms_count,
        ms.suspicious_links_count,
        ms.repeated_sharing,
        ms.high_risk_user,
        ms.score as original_score
    FROM training_feedback tf
    INNER JOIN message_scores ms ON tf.message_id = ms.message_id
    WHERE tf.is_correct IS NOT NULL
";

$result = $conn->query($query);
$feedback_count = 0;
$feedbacks = [];

if ($result) {
    while ($row = $result->fetch_assoc()) {
        $feedbacks[] = $row;
        $feedback_count++;
    }
}

if ($feedback_count >= 10) {
    
    // Analyze each factor
    $factors = [
        "sensitive_terms" => "sensitive_terms_count",
        "suspicious_links" => "suspicious_links_count",
        "repeated_sharing" => "repeated_sharing",
        "high_risk_user" => "high_risk_user"
    ];
    
    foreach ($factors as $factor_name => $db_field) {
        $correct_with_factor = 0;
        $incorrect_with_factor = 0;
        $total_with_factor = 0;
        
        foreach ($feedbacks as $feedback) {
            $has_factor = false;
            if ($db_field == "sensitive_terms_count") {
                $has_factor = $feedback[$db_field] > 0;
            } elseif ($db_field == "suspicious_links_count") {
                $has_factor = $feedback[$db_field] > 0;
            } elseif ($db_field == "repeated_sharing") {
                $has_factor = $feedback[$db_field] == 1;
            } elseif ($db_field == "high_risk_user") {
                $has_factor = $feedback[$db_field] == 1;
            }
            
            if ($has_factor) {
                $total_with_factor++;
                if ($feedback["is_correct"] == 1) {
                    $correct_with_factor++;
                } else {
                    $incorrect_with_factor++;
                }
            }
        }
        
        if ($total_with_factor > 0) {
            $accuracy = $correct_with_factor / $total_with_factor;
            
            // If accuracy is low (< 0.6), reduce weight
            // If high (> 0.85), maintain or slightly increase
            if ($accuracy < 0.6) {
                // Reduce weight by up to 30%
                $adjustment = 1.0 - (0.6 - $accuracy) * 0.5;
                $adjusted_weights[$factor_name] = max(
                    $default_weights[$factor_name] * 0.5,
                    $default_weights[$factor_name] * $adjustment
                );
            } elseif ($accuracy > 0.85) {
                // Slightly increase if very accurate
                $adjusted_weights[$factor_name] = $default_weights[$factor_name] * 1.1;
            }
        }
    }
}

// Get statistics about scores
$statsQuery = "
    SELECT 
        COUNT(*) as total_scored,
        AVG(score) as avg_score,
        MIN(score) as min_score,
        MAX(score) as max_score,
        SUM(CASE WHEN score >= 10 THEN 1 ELSE 0 END) as high_risk_count,
        SUM(CASE WHEN score >= 5 AND score < 10 THEN 1 ELSE 0 END) as medium_risk_count,
        SUM(CASE WHEN score > 0 AND score < 5 THEN 1 ELSE 0 END) as low_risk_count
    FROM message_scores
    WHERE score > 0
";

$statsResult = $conn->query($statsQuery);
$stats = $statsResult ? $statsResult->fetch_assoc() : null;

// Get factor statistics
$factorStatsQuery = "
    SELECT 
        SUM(sensitive_terms_count) as total_sensitive_terms,
        SUM(suspicious_links_count) as total_suspicious_links,
        SUM(repeated_sharing) as total_repeated_sharing,
        SUM(high_risk_user) as total_high_risk_users
    FROM message_scores
    WHERE score > 0
";

$factorStatsResult = $conn->query($factorStatsQuery);
$factorStats = $factorStatsResult ? $factorStatsResult->fetch_assoc() : null;

$conn->close();

echo json_encode([
    "default_weights" => $default_weights,
    "adjusted_weights" => $adjusted_weights,
    "using_adjusted" => $feedback_count >= 10,
    "feedback_count" => $feedback_count,
    "statistics" => $stats,
    "factor_statistics" => $factorStats
]);
?>

