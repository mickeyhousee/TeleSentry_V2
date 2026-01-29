<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Webserver</title>
    <link rel="stylesheet" href="/telegram_webserver/css/styles.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
</head>
<body>
    <div class="sidebar">
        <div class="menu-icon">
            <img src="/telegram_webserver/images/menu.png" alt="Menu">
        </div>
        <div class="logo" onclick="loadRoom('roompred')">
            <img src="/telegram_webserver/images/logo_cociber.png" alt="Logo">
        </div>
        <a href="#" onclick="loadRoom('room3'); return false;">
            <span class="text">SEARCH</span>
        </a>
        <a href="#" onclick="loadRoom('room5'); return false;">
            <span class="text">RANKING</span>
        </a>
        <a href="#" onclick="loadRoom('room2'); return false;">
            <span class="text">BOTS</span>
        </a>
        <a href="#" onclick="loadRoom('room4'); return false;">
            <span class="text">GROUPS</span>
        </a>
        <a href="#" onclick="loadRoom('room6'); return false;">
            <span class="text">TRAINING</span>
        </a>
        <a href="#" onclick="loadRoom('room7'); return false;">
            <span class="text">SCORES</span>
        </a>
    </div>
    <div class="content">
        <div id="roomContent"></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    <script src="/telegram_webserver/js/script.js"></script>
</body>
</html>
