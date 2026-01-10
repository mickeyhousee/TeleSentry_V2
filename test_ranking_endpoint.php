<?php
// Teste simples do endpoint de ranking
$url = "http://localhost/telegram_webserver/php/get_ranking.php?min_score=1&limit=5";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

echo "HTTP Code: $httpCode\n";
echo "Response:\n";
$data = json_decode($response, true);
if ($data) {
    echo "Total de mensagens: " . (isset($data['total']) ? $data['total'] : 0) . "\n";
    echo "Mensagens retornadas: " . (isset($data['messages']) ? count($data['messages']) : 0) . "\n";
    if (isset($data['error'])) {
        echo "Erro: " . $data['error'] . "\n";
    }
} else {
    echo "Resposta não é JSON válido:\n";
    echo substr($response, 0, 500) . "\n";
}
?>

