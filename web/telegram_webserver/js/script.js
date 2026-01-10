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
            case 'room5':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <h2>Ranking de Mensagens que Merecem Atenção</h2>
                        <div style="margin: 20px 0;">
                            <label>Pontuação mínima: </label>
                            <input type="number" id="minScoreInput" value="1" min="1" style="margin: 0 10px; padding: 5px;">
                            <label>Limite: </label>
                            <input type="number" id="limitInput" value="50" min="1" max="200" style="margin: 0 10px; padding: 5px;">
                            <button onclick="loadRanking()" style="padding: 5px 15px; margin-left: 10px;">Carregar</button>
                        </div>
                        <div class="table-container">
                            <table id="rankingTable" class="styled-table">
                                <thead>
                                    <tr>
                                        <th>Pontuação</th>
                                        <th>ID Mensagem</th>
                                        <th>Data</th>
                                        <th>Remetente</th>
                                        <th>Grupo</th>
                                        <th>Conteúdo</th>
                                        <th>Detalhes</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>`;
                
                function loadRanking() {
                    const minScoreInput = document.getElementById('minScoreInput');
                    const limitInput = document.getElementById('limitInput');
                    const tbody = document.querySelector('#rankingTable tbody');
                    
                    if (!tbody) {
                        console.error('Tabela rankingTable não encontrada');
                        return;
                    }
                    
                    const minScore = minScoreInput ? minScoreInput.value || 1 : 1;
                    const limit = limitInput ? limitInput.value || 50 : 50;
                    
                    // Mostra mensagem de carregamento
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Carregando...</td></tr>';
                    
                    console.log('Carregando ranking com min_score:', minScore, 'limit:', limit);
                    fetch(`/telegram_webserver/php/get_ranking.php?min_score=${minScore}&limit=${limit}`, {
                        method: 'GET'
                    })
                    .then(response => {
                        console.log('Response status:', response.status);
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Dados recebidos:', data);
                        tbody.innerHTML = '';

                        if (data.error) {
                            console.error('Erro no servidor:', data.error);
                            tbody.innerHTML = `<tr><td colspan="7" class="error-message">${data.error}</td></tr>`;
                            return;
                        }

                        if (!data.messages || data.messages.length === 0) {
                            console.log('Nenhuma mensagem encontrada');
                            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Nenhuma mensagem encontrada com pontuação acima do mínimo.</td></tr>';
                            return;
                        }

                        console.log('Processando', data.messages.length, 'mensagens');

                        data.messages.forEach(message => {
                            const row = document.createElement('tr');
                            const score = message.score || 0;
                            const scoreClass = score >= 10 ? 'high-score' : score >= 5 ? 'medium-score' : 'low-score';
                            
                            const details = [];
                            if (message.sensitive_terms_count > 0) {
                                details.push(`Termos sensíveis: ${message.sensitive_terms_count}`);
                            }
                            if (message.suspicious_links_count > 0) {
                                details.push(`Links suspeitos: ${message.suspicious_links_count}`);
                            }
                            if (message.repeated_sharing == 1) {
                                details.push('Partilha repetida');
                            }
                            if (message.high_risk_user == 1) {
                                details.push('Usuário high-risk');
                            }
                            
                            const linksHtml = message.links && message.links.length > 0 
                                ? `<br><strong>Links:</strong> ${message.links.map(l => `<a href="${l}" target="_blank" style="color: #4a9eff;">${l}</a>`).join(', ')}`
                                : '';
                            
                            // Escape HTML in content to avoid problems
                            const content = (message.content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            const contentPreview = content.length > 100 ? content.substring(0, 100) + '...' : content;
                            
                            row.innerHTML = `
                                <td><span class="${scoreClass}" style="font-weight: bold; padding: 3px 8px; border-radius: 3px; display: inline-block;">${score}</span></td>
                                <td>${message.id_message}</td>
                                <td>${message.date_message || 'N/A'}</td>
                                <td>${message.sender_name || message.sender_username || 'Unknown'}</td>
                                <td>${message.group_name || 'N/A'}</td>
                                <td class="content-cell">${contentPreview}${linksHtml}</td>
                                <td>${details.join('<br>') || 'N/A'}</td>`;
                            tbody.appendChild(row);
                        });
                    })
                    .catch(error => {
                        console.error('Error fetching ranking:', error);
                        if (tbody) {
                            tbody.innerHTML = `<tr><td colspan="7" class="error-message">Erro ao carregar ranking: ${error.message}</td></tr>`;
                        }
                    });
                }
                
                // Load ranking automatically after a small delay to ensure the DOM is ready
                setTimeout(function() {
                    loadRanking();
                }, 100);
                window.loadRanking = loadRanking;
                break;
            case 'room6':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <h2>Treinamento do Sistema de Pontuação</h2>
                        <div id="trainingStats" style="margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px;">
                            <p>Carregando estatísticas...</p>
                        </div>
                        <div style="margin: 20px 0;">
                            <button onclick="loadTrainingMessage()" style="padding: 10px 20px; font-size: 16px; background: #4a9eff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                Carregar Mensagem Aleatória
                            </button>
                        </div>
                        <div id="trainingMessageContainer" style="margin-top: 20px;"></div>
                    </div>`;
                
                function loadTrainingStats() {
                    fetch('/telegram_webserver/php/get_training_stats.php')
                        .then(response => response.json())
                        .then(data => {
                            const statsDiv = document.getElementById('trainingStats');
                            if (data.error) {
                                statsDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
                                return;
                            }
                            statsDiv.innerHTML = `
                                <h3>Estatísticas de Treinamento</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 10px;">
                                    <div style="padding: 10px; background: white; border-radius: 5px;">
                                        <strong>Total Pontuadas:</strong> ${data.total_scored || 0}
                                    </div>
                                    <div style="padding: 10px; background: white; border-radius: 5px;">
                                        <strong>Revisadas:</strong> ${data.total_reviewed || 0}
                                    </div>
                                    <div style="padding: 10px; background: white; border-radius: 5px;">
                                        <strong>Corretas:</strong> <span style="color: green;">${data.total_correct || 0}</span>
                                    </div>
                                    <div style="padding: 10px; background: white; border-radius: 5px;">
                                        <strong>Incorretas:</strong> <span style="color: red;">${data.total_incorrect || 0}</span>
                                    </div>
                                    <div style="padding: 10px; background: white; border-radius: 5px;">
                                        <strong>Pendentes:</strong> ${data.total_pending || 0}
                                    </div>
                                    <div style="padding: 10px; background: white; border-radius: 5px;">
                                        <strong>Precisão:</strong> ${data.accuracy || 0}%
                                    </div>
                                </div>
                            `;
                        })
                        .catch(error => {
                            console.error('Erro ao carregar estatísticas:', error);
                            document.getElementById('trainingStats').innerHTML = 
                                `<p class="error-message">Erro ao carregar estatísticas: ${error.message}</p>`;
                        });
                }
                
                function loadTrainingMessage() {
                    const container = document.getElementById('trainingMessageContainer');
                    container.innerHTML = '<p>Carregando mensagem...</p>';
                    
                    fetch('/telegram_webserver/php/get_training_message.php?exclude_reviewed=true')
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                container.innerHTML = `<p class="error-message">${data.error}</p>`;
                                return;
                            }
                            
                            if (!data.message) {
                                container.innerHTML = `
                                    <div style="padding: 20px; background: #fff3cd; border-radius: 5px; border: 1px solid #ffc107;">
                                        <p><strong>Nenhuma mensagem disponível para revisão.</strong></p>
                                        <p>Todas as mensagens pontuadas já foram revisadas ou não há mensagens pontuadas no sistema.</p>
                                    </div>
                                `;
                                return;
                            }
                            
                            const message = data.message;
                            const score = message.score || 0;
                            const scoreClass = score >= 10 ? 'high-score' : score >= 5 ? 'medium-score' : 'low-score';
                            
                            const details = [];
                            if (message.sensitive_terms_count > 0) {
                                details.push(`Termos sensíveis: ${message.sensitive_terms_count}`);
                            }
                            if (message.suspicious_links_count > 0) {
                                details.push(`Links suspeitos: ${message.suspicious_links_count}`);
                            }
                            if (message.repeated_sharing == 1) {
                                details.push('Partilha repetida');
                            }
                            if (message.high_risk_user == 1) {
                                details.push('Usuário high-risk');
                            }
                            
                            const linksHtml = message.links && message.links.length > 0 
                                ? `<div style="margin-top: 10px;"><strong>Links:</strong><br>${message.links.map(l => `<a href="${l}" target="_blank" style="color: #4a9eff;">${l}</a>`).join('<br>')}</div>`
                                : '';
                            
                            // Escapa HTML no conteúdo
                            const content = (message.content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            const translatedContent = (message.translated_content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            
                            container.innerHTML = `
                                <div style="padding: 20px; background: white; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 20px;">
                                    <h3>Mensagem para Revisão</h3>
                                    <div style="margin: 15px 0;">
                                        <strong>Pontuação Atual:</strong> 
                                        <span class="${scoreClass}" style="font-weight: bold; padding: 5px 10px; border-radius: 3px; display: inline-block; margin-left: 10px;">
                                            ${score} pontos
                                        </span>
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>ID Mensagem:</strong> ${message.id_message}
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>Data:</strong> ${message.date_message || 'N/A'}
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>Remetente:</strong> ${message.sender_name || message.sender_username || 'Unknown'}
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>Grupo:</strong> ${message.group_name || 'N/A'}
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>Conteúdo:</strong>
                                        <div style="padding: 10px; background: #f9f9f9; border-radius: 3px; margin-top: 5px; white-space: pre-wrap; word-wrap: break-word;">
                                            ${content || '(sem conteúdo)'}
                                        </div>
                                    </div>
                                    ${translatedContent ? `
                                    <div style="margin: 15px 0;">
                                        <strong>Conteúdo Traduzido:</strong>
                                        <div style="padding: 10px; background: #f9f9f9; border-radius: 3px; margin-top: 5px; white-space: pre-wrap; word-wrap: break-word;">
                                            ${translatedContent}
                                        </div>
                                    </div>
                                    ` : ''}
                                    ${linksHtml}
                                    <div style="margin: 15px 0;">
                                        <strong>Detalhes da Pontuação:</strong>
                                        <ul style="margin-top: 5px;">
                                            ${details.map(d => `<li>${d}</li>`).join('')}
                                        </ul>
                                    </div>
                                    
                                    <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd;">
                                        <h4>A pontuação está correta?</h4>
                                        <div style="margin: 15px 0;">
                                            <button onclick="submitFeedback(${message.id_message}, ${score}, true)" 
                                                    style="padding: 10px 30px; font-size: 16px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
                                                ✓ Sim, está correta
                                            </button>
                                            <button onclick="submitFeedback(${message.id_message}, ${score}, false)" 
                                                    style="padding: 10px 30px; font-size: 16px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                                ✗ Não, está incorreta
                                            </button>
                                        </div>
                                        <div style="margin-top: 15px;">
                                            <label><strong>Notas adicionais (opcional):</strong></label><br>
                                            <textarea id="feedbackNotes" rows="3" style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ddd; border-radius: 3px; font-family: inherit;"></textarea>
                                        </div>
                                    </div>
                                </div>
                            `;
                        })
                        .catch(error => {
                            console.error('Erro ao carregar mensagem:', error);
                            container.innerHTML = `<p class="error-message">Erro ao carregar mensagem: ${error.message}</p>`;
                        });
                }
                
                function submitFeedback(messageId, originalScore, isCorrect) {
                    const notes = document.getElementById('feedbackNotes') ? document.getElementById('feedbackNotes').value : '';
                    
                    fetch('/telegram_webserver/php/save_training_feedback.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message_id: messageId,
                            original_score: originalScore,
                            is_correct: isCorrect,
                            feedback_notes: notes
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert('Erro ao salvar feedback: ' + data.error);
                            return;
                        }
                        
                        const container = document.getElementById('trainingMessageContainer');
                        container.innerHTML = `
                            <div style="padding: 20px; background: ${isCorrect ? '#d4edda' : '#f8d7da'}; border-radius: 5px; border: 1px solid ${isCorrect ? '#c3e6cb' : '#f5c6cb'};">
                                <p><strong>Feedback salvo com sucesso!</strong></p>
                                <p>A pontuação foi marcada como ${isCorrect ? 'correta' : 'incorreta'}.</p>
                                <button onclick="loadTrainingMessage(); loadTrainingStats();" 
                                        style="padding: 10px 20px; margin-top: 10px; background: #4a9eff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                    Carregar Próxima Mensagem
                                </button>
                            </div>
                        `;
                        
                        // Atualizar estatísticas
                        loadTrainingStats();
                    })
                    .catch(error => {
                        console.error('Erro ao salvar feedback:', error);
                        alert('Erro ao salvar feedback: ' + error.message);
                    });
                }
                
                // Carregar estatísticas ao abrir a página
                loadTrainingStats();
                window.loadTrainingMessage = loadTrainingMessage;
                window.submitFeedback = submitFeedback;
                break;
            default:
                roomContent.innerHTML = '<h2>Bem-vindo</h2><p>Escolha uma sala na barra de navegação lateral.</p>';
        }
    }
    window.loadRoom = loadRoom;

    // Carregar a sala de predefinição ao iniciar a página
    loadRoom('roompred');
});
