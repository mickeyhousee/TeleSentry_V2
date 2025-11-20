document.addEventListener("DOMContentLoaded", function() {
    function loadRoom(room) {
        const roomContent = document.getElementById('roomContent');
        switch (room) {
            case 'room1':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <table id="resultTable" class="styled-table display" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Data</th>
                                    <th>Conteúdo</th>
                                    <th>Conteúdo Traduzido</th>
                                    <th>Utilizador</th>
                                    <th>Grupo</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>`;
                
                // Inicializar DataTables após o conteúdo HTML ser adicionado
                $(document).ready(function() {
                    $('#resultTable').DataTable({
                        "ajax": {
                            "url": "/telegram_webserver/php/search.php",
                            "type": "POST",
                            "dataSrc": ""
                        },
                        "columns": [
                            { "data": "id_message" },
                            { "data": "date_message" },
                            { "data": "content" },
                            { "data": "translated_content" },
                            { "data": "id_user" }, // Este campo agora conterá o username
                            { "data": "group_name" } // Este campo agora conterá o nome do grupo
                        ],
                        "pageLength": 10, // Definindo o número de linhas por página
                        "dom": '<"top"f>rt<"bottom"lip><"clear">',
                        "language": {
                            "search": "Procurar:",
                            "lengthMenu": "Mostrar _MENU_ entradas",
                            "info": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
                            "paginate": {
                                "first": "Primeiro",
                                "last": "Último",
                                "next": "Próximo",
                                "previous": "Anterior"
                            }
                        }
                    });
                });
                break;
            case 'room2':
                fetch('/telegram_webserver/php/get_bots.php', {
                    method: 'GET'
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Response data:', data); // Adicionando log para ver a resposta
                    if (Array.isArray(data)) {
                        let botsContent = '<div class="bots-grid">';
                        data.forEach(bot => {
                            botsContent += `
                                <div class="bot-card">
                                    <h3>${bot.bot_name}</h3>
                                    <p><strong>ID:</strong> ${bot.bot_id}</p>
                                    <p><strong>Grupos:</strong> ${bot.groups || 'Nenhum grupo'}</p>
                                    <p><strong>ID dos Grupos:</strong> ${bot.group_ids || 'Nenhum grupo'}</p>
                                    <p><strong>Mensagens:</strong> ${bot.message_count}</p>
                                </div>`;
                        });
                        botsContent += '</div>';
                        roomContent.innerHTML = botsContent;
                    } else {
                        console.error('Expected an array but got:', data);
                        roomContent.innerHTML = `<p class="error-message">Erro ao carregar dados dos bots.</p>`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching bots:', error);
                    roomContent.innerHTML = `<p class="error-message">Erro ao carregar dados dos bots.</p>`;
                });
                break;
            case 'room3':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <input type="text" id="searchInput" placeholder="Pesquisar mensagens...">
                        <div class="table-container">
                            <table id="customTable" class="styled-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Data</th>
                                        <th>Conteúdo</th>
                                        <th>Conteúdo Traduzido</th>
                                        <th>Utilizador</th>
                                        <th>Grupo</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                        <div id="pagination" class="pagination"></div>
                    </div>`;
                
                loadMessages(1);

                document.getElementById('searchInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        loadMessages(1, e.target.value);
                    }
                });

                function loadMessages(page, query = '') {
                    fetch(`/telegram_webserver/php/search.php?page=${page}&query=${encodeURIComponent(query)}`, {
                        method: 'GET'
                    })
                    .then(response => response.json())
                    .then(data => {
                        const tbody = document.querySelector('#customTable tbody');
                        tbody.innerHTML = '';

                        data.messages.forEach(message => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${message.id_message}</td>
                                <td>${message.date_message}</td>
                                <td class="content-cell">${message.content}</td>
                                <td class="content-cell">${message.translated_content}</td>
                                <td>${message.id_user}</td>
                                <td>${message.group_name}</td>`;
                            tbody.appendChild(row);
                        });

                        const pagination = document.getElementById('pagination');
                        pagination.innerHTML = '';

                        const prevLink = document.createElement('a');
                        prevLink.href = '#';
                        prevLink.textContent = 'Anterior';
                        prevLink.classList.add('page-link');
                        if (page === 1) prevLink.classList.add('disabled');
                        prevLink.addEventListener('click', (e) => {
                            e.preventDefault();
                            if (page > 1) loadMessages(page - 1, query);
                        });
                        pagination.appendChild(prevLink);

                        const nextLink = document.createElement('a');
                        nextLink.href = '#';
                        nextLink.textContent = 'Próximo';
                        nextLink.classList.add('page-link');
                        if (page === data.totalPages) nextLink.classList.add('disabled');
                        nextLink.addEventListener('click', (e) => {
                            e.preventDefault();
                            if (page < data.totalPages) loadMessages(page + 1, query);
                        });
                        pagination.appendChild(nextLink);
                    })
                    .catch(error => console.error('Error fetching messages:', error));
                }

                break;
            case 'room4':
                fetch('/telegram_webserver/php/get_groups.php', {
                    method: 'GET'
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Response data:', data); // Adicionando log para ver a resposta
                    if (Array.isArray(data)) {
                        let groupsContent = '<div class="bots-grid">';
                        data.forEach(group => {
                            groupsContent += `
                                <div class="bot-card">
                                    <h3>${group.group_name}</h3>
                                    <p><strong>ID:</strong> ${group.group_id}</p>
                                    <p><strong>Mensagens:</strong> ${group.message_count}</p>
                                </div>`;
                        });
                        groupsContent += '</div>';
                        roomContent.innerHTML = groupsContent;
                    } else {
                        console.error('Expected an array but got:', data);
                        roomContent.innerHTML = `<p class="error-message">Erro ao carregar dados dos grupos.</p>`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching groups:', error);
                    roomContent.innerHTML = `<p class="error-message">Erro ao carregar dados dos grupos.</p>`;
                });
                break;
            default:
                roomContent.innerHTML = '<h2>Bem-vindo</h2><p>Escolha uma sala na barra de navegação lateral.</p>';
        }
    }
    window.loadRoom = loadRoom;

    // Carregar a sala de predefinição ao iniciar a página
    loadRoom('roompred');
});
