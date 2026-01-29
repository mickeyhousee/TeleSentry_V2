document.addEventListener("DOMContentLoaded", function() {
    function loadRoom(room) {
        const roomContent = document.getElementById('roomContent');
        
        // Cleanup training room auto-refresh if leaving room6
        if (room !== 'room6' && window.trainingRoomState && window.trainingRoomState.autoRefreshInterval) {
            clearInterval(window.trainingRoomState.autoRefreshInterval);
            window.trainingRoomState.autoRefreshInterval = null;
        }
        
        switch (room) {
            case 'room1':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <table id="resultTable" class="styled-table display" style="width:100%;">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Date</th>
                                    <th>Content</th>
                                    <th>Translated Content</th>
                                    <th>User</th>
                                    <th>Group</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>`;
                
                // Initialize DataTables after HTML content is added
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
                            { "data": "id_user" }, // This field will now contain the username
                            { "data": "group_name" } // This field will now contain the group name
                        ],
                        "pageLength": 10, // Setting the number of rows per page
                        "dom": '<"top"f>rt<"bottom"lip><"clear">',
                        "language": {
                            "search": "Search:",
                            "lengthMenu": "Show _MENU_ entries",
                            "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                            "paginate": {
                                "first": "First",
                                "last": "Last",
                                "next": "Next",
                                "previous": "Previous"
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
                    console.log('Response data:', data); // Adding log to see the response
                    if (Array.isArray(data)) {
                        let botsContent = '<div class="bots-grid">';
                        data.forEach(bot => {
                            botsContent += `
                                <div class="bot-card">
                                    <h3>${bot.bot_name}</h3>
                                    <p><strong>ID:</strong> ${bot.bot_id}</p>
                                    <p><strong>Groups:</strong> ${bot.groups || 'No groups'}</p>
                                    <p><strong>Group IDs:</strong> ${bot.group_ids || 'No groups'}</p>
                                    <p><strong>Messages:</strong> ${bot.message_count}</p>
                                </div>`;
                        });
                        botsContent += '</div>';
                        roomContent.innerHTML = botsContent;
                    } else {
                        console.error('Expected an array but got:', data);
                        roomContent.innerHTML = `<p class="error-message">Error loading bot data.</p>`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching bots:', error);
                    roomContent.innerHTML = `<p class="error-message">Error loading bot data.</p>`;
                });
                break;
            case 'room3':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <input type="text" id="searchInput" placeholder="Search messages...">
                        <div class="table-container">
                            <table id="customTable" class="styled-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Date</th>
                                        <th>Content</th>
                                        <th>Translated Content</th>
                                        <th>User</th>
                                        <th>Group</th>
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
                        prevLink.textContent = 'Previous';
                        prevLink.classList.add('page-link');
                        if (page === 1) prevLink.classList.add('disabled');
                        prevLink.addEventListener('click', (e) => {
                            e.preventDefault();
                            if (page > 1) loadMessages(page - 1, query);
                        });
                        pagination.appendChild(prevLink);

                        const nextLink = document.createElement('a');
                        nextLink.href = '#';
                        nextLink.textContent = 'Next';
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
                    console.log('Response data:', data); // Adding log to see the response
                    if (Array.isArray(data)) {
                        let groupsContent = '<div class="bots-grid">';
                        data.forEach(group => {
                            groupsContent += `
                                <div class="bot-card">
                                    <h3>${group.group_name}</h3>
                                    <p><strong>ID:</strong> ${group.group_id}</p>
                                    <p><strong>Messages:</strong> ${group.message_count}</p>
                                </div>`;
                        });
                        groupsContent += '</div>';
                        roomContent.innerHTML = groupsContent;
                    } else {
                        console.error('Expected an array but got:', data);
                        roomContent.innerHTML = `<p class="error-message">Error loading group data.</p>`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching groups:', error);
                    roomContent.innerHTML = `<p class="error-message">Error loading group data.</p>`;
                });
                break;
            case 'room5':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <h2>Ranking of Messages Requiring Attention</h2>
                        <div style="margin: 20px 0;">
                            <label>Minimum score: </label>
                            <input type="number" id="minScoreInput" value="1" min="1" style="margin: 0 10px; padding: 5px;">
                            <label>Limit: </label>
                            <input type="number" id="limitInput" value="50" min="1" max="200" style="margin: 0 10px; padding: 5px;">
                            <button onclick="loadRanking()" style="padding: 5px 15px; margin-left: 10px;">Load</button>
                        </div>
                        <div class="table-container">
                            <table id="rankingTable" class="styled-table">
                                <thead>
                                    <tr>
                                        <th>Score</th>
                                        <th>Message ID</th>
                                        <th>Date</th>
                                        <th>Sender</th>
                                        <th>Group</th>
                                        <th>Content</th>
                                        <th>Details</th>
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
                        console.error('rankingTable not found');
                        return;
                    }
                    
                    const minScore = minScoreInput ? minScoreInput.value || 1 : 1;
                    const limit = limitInput ? limitInput.value || 50 : 50;
                    
                    // Show loading message
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Loading...</td></tr>';
                    
                    console.log('Loading ranking with min_score:', minScore, 'limit:', limit);
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
                        console.log('Data received:', data);
                        tbody.innerHTML = '';

                        if (data.error) {
                            console.error('Server error:', data.error);
                            tbody.innerHTML = `<tr><td colspan="7" class="error-message">${data.error}</td></tr>`;
                            return;
                        }

                        if (!data.messages || data.messages.length === 0) {
                            console.log('No messages found');
                            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No messages found with score above minimum.</td></tr>';
                            return;
                        }

                        console.log('Processing', data.messages.length, 'messages');

                        data.messages.forEach(message => {
                            const row = document.createElement('tr');
                            const score = message.score || 0;
                            const scoreClass = score >= 10 ? 'high-score' : score >= 5 ? 'medium-score' : 'low-score';
                            
                            const details = [];
                            if (message.sensitive_terms_count > 0) {
                                details.push(`Sensitive terms: ${message.sensitive_terms_count}`);
                            }
                            if (message.suspicious_links_count > 0) {
                                details.push(`Suspicious links: ${message.suspicious_links_count}`);
                            }
                            if (message.repeated_sharing == 1) {
                                details.push('Repeated sharing');
                            }
                            if (message.high_risk_user == 1) {
                                details.push('High-risk user');
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
                            tbody.innerHTML = `<tr><td colspan="7" class="error-message">Error loading ranking: ${error.message}</td></tr>`;
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
                        <h2>Scoring System Training</h2>
                        <div id="trainingStats" style="margin: 20px 0; padding: 15px; background: #2e2e2e; border-radius: 5px; color: #ffffff;">
                            <p style="color: #ffffff;">Loading statistics...</p>
                        </div>
                        <div style="margin: 20px 0;">
                            <button onclick="loadTrainingMessage()" style="padding: 10px 20px; font-size: 16px; background: #4a9eff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                Load Random Message
                            </button>
                            <label style="margin-left: 20px; color: #ffffff;">
                                <input type="checkbox" id="autoRefreshCheckbox" checked style="margin-right: 5px;">
                                Auto-refresh (every 15 seconds)
                            </label>
                        </div>
                        <div id="trainingMessageContainer" style="margin-top: 20px;"></div>
                    </div>`;
                
                // Variable to store current message ID and polling interval
                // Use window object to persist across room switches
                if (!window.trainingRoomState) {
                    window.trainingRoomState = {
                        currentMessageId: null,
                        autoRefreshInterval: null
                    };
                }
                let currentMessageId = window.trainingRoomState.currentMessageId;
                let autoRefreshInterval = window.trainingRoomState.autoRefreshInterval;
                
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
                                <h3 style="color: #ffffff;">Training Statistics</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 10px;">
                                    <div style="padding: 10px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                        <strong style="color: #ffffff;">Total Scored:</strong> ${data.total_scored || 0}
                                    </div>
                                    <div style="padding: 10px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                        <strong style="color: #ffffff;">Reviewed:</strong> ${data.total_reviewed || 0}
                                    </div>
                                    <div style="padding: 10px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                        <strong style="color: #ffffff;">Correct:</strong> <span style="color: #4ade80;">${data.total_correct || 0}</span>
                                    </div>
                                    <div style="padding: 10px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                        <strong style="color: #ffffff;">Incorrect:</strong> <span style="color: #f87171;">${data.total_incorrect || 0}</span>
                                    </div>
                                    <div style="padding: 10px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                        <strong style="color: #ffffff;">Pending:</strong> ${data.total_pending || 0}
                                    </div>
                                    <div style="padding: 10px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                        <strong style="color: #ffffff;">Accuracy:</strong> ${data.accuracy || 0}%
                                    </div>
                                </div>
                            `;
                        })
                        .catch(error => {
                            console.error('Error loading statistics:', error);
                            document.getElementById('trainingStats').innerHTML = 
                                `<p class="error-message">Error loading statistics: ${error.message}</p>`;
                        });
                }
                
                function loadTrainingMessage(forceLoad = false) {
                    const container = document.getElementById('trainingMessageContainer');
                    
                    // Don't reload if there's already a message being reviewed and not forcing
                    if (!forceLoad && currentMessageId !== null && container.innerHTML && 
                        !container.innerHTML.includes('No messages available') && 
                        !container.innerHTML.includes('Feedback saved successfully')) {
                        return;
                    }
                    
                    container.innerHTML = '<p style="color: #ffffff;">Loading message...</p>';
                    
                    fetch('/telegram_webserver/php/get_training_message.php?exclude_reviewed=true')
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                container.innerHTML = `<p class="error-message">${data.error}</p>`;
                                currentMessageId = null;
                                window.trainingRoomState.currentMessageId = null;
                                return;
                            }
                            
                            if (!data.message) {
                                container.innerHTML = `
                                    <div style="padding: 20px; background: #3a3a3a; border-radius: 5px; border: 1px solid #ffa500; color: #ffffff;">
                                        <p style="color: #ffffff;"><strong>No messages available for review.</strong></p>
                                        <p style="color: #ffffff;">All scored messages have been reviewed or there are no scored messages in the system.</p>
                                    </div>
                                `;
                                currentMessageId = null;
                                window.trainingRoomState.currentMessageId = null;
                                return;
                            }
                            
                            const message = data.message;
                            // Only update currentMessageId if it's different (new message)
                            if (currentMessageId !== message.id_message) {
                                currentMessageId = message.id_message;
                                window.trainingRoomState.currentMessageId = currentMessageId;
                            }
                            const score = message.score || 0;
                            const scoreClass = score >= 10 ? 'high-score' : score >= 5 ? 'medium-score' : 'low-score';
                            
                            const details = [];
                            if (message.sensitive_terms_count > 0) {
                                details.push(`Sensitive terms: ${message.sensitive_terms_count}`);
                            }
                            if (message.suspicious_links_count > 0) {
                                details.push(`Suspicious links: ${message.suspicious_links_count}`);
                            }
                            if (message.repeated_sharing == 1) {
                                details.push('Repeated sharing');
                            }
                            if (message.high_risk_user == 1) {
                                details.push('High-risk user');
                            }
                            
                            const linksHtml = message.links && message.links.length > 0 
                                ? `<div style="margin-top: 10px; color: #ffffff;"><strong style="color: #ffffff;">Links:</strong><br>${message.links.map(l => `<a href="${l}" target="_blank" style="color: #4a9eff;">${l}</a>`).join('<br>')}</div>`
                                : '';
                            
                            // Escape HTML in content
                            const content = (message.content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            const translatedContent = (message.translated_content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            
                            container.innerHTML = `
                                <div style="padding: 20px; background: #3a3a3a; border-radius: 5px; border: 1px solid #555; margin-bottom: 20px; color: #ffffff;">
                                    <h3 style="color: #ffffff;">Message for Review</h3>
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Current Score:</strong> 
                                        <span class="${scoreClass}" style="font-weight: bold; padding: 5px 10px; border-radius: 3px; display: inline-block; margin-left: 10px;">
                                            ${score} points
                                        </span>
                                    </div>
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Message ID:</strong> ${message.id_message}
                                    </div>
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Date:</strong> ${message.date_message || 'N/A'}
                                    </div>
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Sender:</strong> ${message.sender_name || message.sender_username || 'Unknown'}
                                    </div>
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Group:</strong> ${message.group_name || 'N/A'}
                                    </div>
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Content:</strong>
                                        <div style="padding: 10px; background: #2e2e2e; border-radius: 3px; margin-top: 5px; white-space: pre-wrap; word-wrap: break-word; color: #ffffff;">
                                            ${content || '(no content)'}
                                        </div>
                                    </div>
                                    ${translatedContent ? `
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Translated Content:</strong>
                                        <div style="padding: 10px; background: #2e2e2e; border-radius: 3px; margin-top: 5px; white-space: pre-wrap; word-wrap: break-word; color: #ffffff;">
                                            ${translatedContent}
                                        </div>
                                    </div>
                                    ` : ''}
                                    ${linksHtml}
                                    <div style="margin: 15px 0; color: #ffffff;">
                                        <strong style="color: #ffffff;">Score Details:</strong>
                                        <ul style="margin-top: 5px; color: #ffffff;">
                                            ${details.map(d => `<li style="color: #ffffff;">${d}</li>`).join('')}
                                        </ul>
                                    </div>
                                    
                                    <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #555;">
                                        <h4 style="color: #ffffff;">Is the score correct?</h4>
                                        <div style="margin: 15px 0;">
                                            <button onclick="submitFeedback(${message.id_message}, ${score}, true)" 
                                                    style="padding: 10px 30px; font-size: 16px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
                                                ✓ Yes, it's correct
                                            </button>
                                            <button onclick="submitFeedback(${message.id_message}, ${score}, false)" 
                                                    style="padding: 10px 30px; font-size: 16px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                                ✗ No, it's incorrect
                                            </button>
                                        </div>
                                        <div style="margin-top: 15px;">
                                            <label style="color: #ffffff;"><strong>Additional notes (optional):</strong></label><br>
                                            <textarea id="feedbackNotes" rows="3" style="width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #555; border-radius: 3px; font-family: inherit; background: #2e2e2e; color: #ffffff;"></textarea>
                                        </div>
                                    </div>
                                </div>
                            `;
                        })
                        .catch(error => {
                            console.error('Error loading message:', error);
                            container.innerHTML = `<p class="error-message">Error loading message: ${error.message}</p>`;
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
                            alert('Error saving feedback: ' + data.error);
                            return;
                        }
                        
                        const container = document.getElementById('trainingMessageContainer');
                        container.innerHTML = `
                            <div style="padding: 20px; background: ${isCorrect ? '#1e3a1e' : '#3a1e1e'}; border-radius: 5px; border: 1px solid ${isCorrect ? '#4ade80' : '#f87171'}; color: #ffffff;">
                                <p style="color: #ffffff;"><strong>Feedback saved successfully!</strong></p>
                                <p style="color: #ffffff;">The score was marked as ${isCorrect ? 'correct' : 'incorrect'}.</p>
                                <button onclick="loadTrainingMessage(true); loadTrainingStats();" 
                                        style="padding: 10px 20px; margin-top: 10px; background: #4a9eff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                                    Load Next Message
                                </button>
                            </div>
                        `;
                        
                        // Reset current message ID so auto-refresh can load a new one
                        currentMessageId = null;
                        window.trainingRoomState.currentMessageId = null;
                        
                        // Update statistics
                        loadTrainingStats();
                        
                        // Auto-load next message after 2 seconds if auto-refresh is enabled
                        setTimeout(function() {
                            const checkbox = document.getElementById('autoRefreshCheckbox');
                            if (checkbox && checkbox.checked) {
                                loadTrainingMessage(true);
                            }
                        }, 2000);
                    })
                    .catch(error => {
                        console.error('Error saving feedback:', error);
                        alert('Error saving feedback: ' + error.message);
                    });
                }
                
                // Function to check for new messages and auto-load if container is empty or showing "no messages"
                function checkForNewMessages() {
                    const checkbox = document.getElementById('autoRefreshCheckbox');
                    if (!checkbox || !checkbox.checked) {
                        return;
                    }
                    
                    const container = document.getElementById('trainingMessageContainer');
                    const containerText = container ? container.innerHTML : '';
                    
                    // Only auto-load if container is empty, showing "no messages", or showing success message
                    if (!containerText || 
                        containerText.includes('No messages available') || 
                        containerText.includes('Feedback saved successfully') ||
                        containerText.includes('Loading message...')) {
                        loadTrainingMessage(true);
                    }
                    
                    // Always update statistics
                    loadTrainingStats();
                }
                
                // Start auto-refresh polling (every 15 seconds)
                function startAutoRefresh() {
                    if (autoRefreshInterval) {
                        clearInterval(autoRefreshInterval);
                    }
                    autoRefreshInterval = setInterval(checkForNewMessages, 15000);
                    window.trainingRoomState.autoRefreshInterval = autoRefreshInterval;
                }
                
                // Stop auto-refresh
                function stopAutoRefresh() {
                    if (autoRefreshInterval) {
                        clearInterval(autoRefreshInterval);
                        autoRefreshInterval = null;
                        window.trainingRoomState.autoRefreshInterval = null;
                    }
                }
                
                // Setup checkbox event listener
                setTimeout(function() {
                    const checkbox = document.getElementById('autoRefreshCheckbox');
                    if (checkbox) {
                        checkbox.addEventListener('change', function() {
                            if (this.checked) {
                                startAutoRefresh();
                                // Check immediately when enabled
                                checkForNewMessages();
                            } else {
                                stopAutoRefresh();
                            }
                        });
                    }
                }, 100);
                
                // Load statistics when opening the page
                loadTrainingStats();
                // Load initial message
                loadTrainingMessage(true);
                // Start auto-refresh
                startAutoRefresh();
                
                window.loadTrainingMessage = loadTrainingMessage;
                window.submitFeedback = submitFeedback;
                
                // Cleanup any existing interval before starting a new one
                if (autoRefreshInterval) {
                    stopAutoRefresh();
                }
                
                break;
            case 'room7':
                roomContent.innerHTML = `
                    <div class="room-content">
                        <img src="/telegram_webserver/images/logo_cociber.png" alt="Logotipo">
                        <h2>Scores and System Parameters</h2>
                        
                        <div id="scoringParamsContainer" style="margin: 20px 0; padding: 20px; background: #2e2e2e; border-radius: 5px; color: #ffffff;">
                            <h3 style="color: #ffffff;">Scoring System Parameters</h3>
                            <p style="color: #ffffff;">Loading parameters...</p>
                        </div>
                    </div>`;
                
                function loadScoringParams() {
                    fetch('/telegram_webserver/php/get_scoring_params.php')
                        .then(response => response.json())
                        .then(data => {
                            const container = document.getElementById('scoringParamsContainer');
                            if (data.error) {
                                container.innerHTML = `<p class="error-message">${data.error}</p>`;
                                return;
                            }
                            
                            const weights = data.using_adjusted ? data.adjusted_weights : data.default_weights;
                            const weightsLabel = data.using_adjusted ? 'Adjusted (based on training)' : 'Default';
                            
                            container.innerHTML = `
                                <h3 style="color: #ffffff;">Scoring System Parameters</h3>
                                <div style="margin-top: 15px;">
                                    <p style="color: #ffffff;"><strong>Current Weights:</strong> ${weightsLabel}</p>
                                    <p style="font-size: 0.9em; color: #cccccc;">${data.feedback_count} training feedbacks available</p>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                                    <div style="padding: 15px; background: #3a3a3a; border-radius: 5px; border-left: 4px solid #4a9eff; color: #ffffff;">
                                        <strong style="color: #ffffff;">Sensitive Terms:</strong><br>
                                        <span style="font-size: 1.2em; color: #4a9eff;">${weights.sensitive_terms.toFixed(2)}</span> points/term
                                        ${data.using_adjusted ? `<br><small style="color: #cccccc;">Default: ${data.default_weights.sensitive_terms.toFixed(2)}</small>` : ''}
                                    </div>
                                    <div style="padding: 15px; background: #3a3a3a; border-radius: 5px; border-left: 4px solid #ff6b6b; color: #ffffff;">
                                        <strong style="color: #ffffff;">Suspicious Links:</strong><br>
                                        <span style="font-size: 1.2em; color: #ff6b6b;">${weights.suspicious_links.toFixed(2)}</span> points/link
                                        ${data.using_adjusted ? `<br><small style="color: #cccccc;">Default: ${data.default_weights.suspicious_links.toFixed(2)}</small>` : ''}
                                    </div>
                                    <div style="padding: 15px; background: #3a3a3a; border-radius: 5px; border-left: 4px solid #ffa500; color: #ffffff;">
                                        <strong style="color: #ffffff;">Repeated Sharing:</strong><br>
                                        <span style="font-size: 1.2em; color: #ffa500;">${weights.repeated_sharing.toFixed(2)}</span> points
                                        ${data.using_adjusted ? `<br><small style="color: #cccccc;">Default: ${data.default_weights.repeated_sharing.toFixed(2)}</small>` : ''}
                                    </div>
                                    <div style="padding: 15px; background: #3a3a3a; border-radius: 5px; border-left: 4px solid #9b59b6; color: #ffffff;">
                                        <strong style="color: #ffffff;">High-Risk User:</strong><br>
                                        <span style="font-size: 1.2em; color: #9b59b6;">${weights.high_risk_user.toFixed(2)}</span> points
                                        ${data.using_adjusted ? `<br><small style="color: #cccccc;">Default: ${data.default_weights.high_risk_user.toFixed(2)}</small>` : ''}
                                    </div>
                                </div>
                                ${data.factor_statistics ? `
                                <div style="margin-top: 20px; padding: 15px; background: #3a3a3a; border-radius: 5px; color: #ffffff;">
                                    <h4 style="color: #ffffff;">Statistics by Factor</h4>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px; color: #ffffff;">
                                        <div style="color: #ffffff;"><strong>Total Sensitive Terms:</strong> ${data.factor_statistics.total_sensitive_terms || 0}</div>
                                        <div style="color: #ffffff;"><strong>Total Suspicious Links:</strong> ${data.factor_statistics.total_suspicious_links || 0}</div>
                                        <div style="color: #ffffff;"><strong>Total Repeated Sharing:</strong> ${data.factor_statistics.total_repeated_sharing || 0}</div>
                                        <div style="color: #ffffff;"><strong>Total High-Risk Users:</strong> ${data.factor_statistics.total_high_risk_users || 0}</div>
                                    </div>
                                </div>
                                ` : ''}
                            `;
                        })
                        .catch(error => {
                            console.error('Error loading parameters:', error);
                            document.getElementById('scoringParamsContainer').innerHTML = 
                                `<p class="error-message">Error loading parameters: ${error.message}</p>`;
                        });
                }
                
                // Load parameters automatically
                loadScoringParams();
                break;
            default:
                roomContent.innerHTML = '<h2>Welcome</h2><p>Choose a room from the side navigation bar.</p>';
        }
    }
    window.loadRoom = loadRoom;

    // Load the default room when starting the page
    loadRoom('roompred');
});
