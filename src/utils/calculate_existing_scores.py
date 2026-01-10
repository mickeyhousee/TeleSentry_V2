"""
Script para calcular pontuações de mensagens existentes no banco de dados.
Execute este script após criar a tabela message_scores para pontuar mensagens antigas.

Uso:
    python3 calculate_existing_scores.py
    
    Ou com credenciais customizadas:
    DB_HOST=localhost DB_USER=grilo DB_PASSWORD=grilo DB_NAME=search_telegram python3 calculate_existing_scores.py
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import DB_CONFIG, but use default values if not available
try:
    from config.settings import DB_CONFIG
except ImportError:
    DB_CONFIG = {}

from services.database import insert_score_to_db
from services.scoring import calculate_message_score, get_high_risk_users
import mysql.connector


async def calculate_all_scores():
    """
    Calculate scores for all messages existing in the database.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    # Check if the database configuration is defined
    # Allow overriding with environment variables
    db_config = {
        "host": os.getenv("DB_HOST") or DB_CONFIG.get("host") or "localhost",
        "user": os.getenv("DB_USER") or DB_CONFIG.get("user") or "grilo",
        "password": os.getenv("DB_PASSWORD") or DB_CONFIG.get("password") or "grilo",
        "database": os.getenv("DB_NAME") or DB_CONFIG.get("database") or "search_telegram",
    }
    
    if not all([db_config["host"], db_config["user"], db_config["database"]]):
        logging.error("Database configuration not found!")
        logging.error("Define the variables DB_HOST, DB_USER, DB_PASSWORD and DB_NAME")
        logging.error("Or create a .env file in the project root")
        return
    
    try:
        # Try to connect to the database
        logging.info(f"Conectando ao banco de dados: {db_config['host']}/{db_config['database']} como {db_config['user']}")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Search all messages
        query = """
            SELECT 
                c.id_message,
                c.date_message,
                c.content,
                c.translated_content,
                u.username as sender_username,
                u.name as sender_name,
                g.group_name
            FROM content c
            LEFT JOIN `user` u ON c.id_user = u.id_user
            LEFT JOIN `group` g ON c.id_group = g.group_id
            ORDER BY c.id_message
        """
        
        cursor.execute(query)
        messages = cursor.fetchall()
        
        # Search links for each message
        link_query = "SELECT link FROM links WHERE message_id = %s"
        
        # Get list of high-risk users once
        high_risk_users = get_high_risk_users(db_config)
        logging.info(f"High-risk users identified: {len(high_risk_users)}")
        
        total = len(messages)
        processed = 0
        scored = 0
        
        logging.info(f"Starting score calculation for {total} messages...")
        
        for message in messages:
            # Search links for the message
            cursor.execute(link_query, (message['id_message'],))
            links = [row['link'] for row in cursor.fetchall()]
            
            # Prepare message data in the expected format
            message_data = {
                "message_id": message['id_message'],
                "date": message['date_message'],
                "content": message['content'] or "",
                "translated_content": message['translated_content'] or "",
                "sender_username": message['sender_username'] or "Unknown",
                "sender": message['sender_name'] or "Unknown",
                "group_name": message['group_name'] or "N/A",
                "in_message_urls": links,
                "attached_files": []
            }
            
            # Calculate score
            try:
                score_details = calculate_message_score(message_data, db_config, high_risk_users)
                
                # Insert score only if it is greater than 0
                if score_details["total_score"] > 0:
                    await insert_score_to_db(message_data["message_id"], score_details, db_config)
                    scored += 1
                    if scored % 10 == 0:
                        logging.info(f"Processed {processed + 1}/{total} messages, {scored} with score > 0")
                
                processed += 1
                
            except Exception as exc:
                logging.error(f"Error calculating score for message {message['id_message']}: {exc}")
                processed += 1
        
        cursor.close()
        conn.close()
        
        logging.info(f"Process completed! {processed}/{total} messages processed, {scored} with score > 0")
        
    except mysql.connector.Error as exc:
        logging.error(f"Database connection error: {exc}")
        logging.error("Check:")
        logging.error("1. If MySQL/MariaDB is running: sudo systemctl status mysql")
        logging.error("2. If the credentials in the .env file are correct")
        logging.error("3. If the user has permissions to access the database")
        logging.error("4. If you need to use 'sudo mysql' or another authentication method")
        raise
    except Exception as exc:
        logging.error(f"Error processing messages: {exc}")
        raise


if __name__ == "__main__":
    asyncio.run(calculate_all_scores())

