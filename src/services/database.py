import logging
import random
import mysql.connector


async def insert_score_to_db(message_id: int, score_details: dict, db_config: dict) -> None:
    """
    Insert score details into the database.
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        score_query = """
            INSERT INTO message_scores 
            (message_id, score, sensitive_terms_count, suspicious_links_count, repeated_sharing, high_risk_user)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                score = VALUES(score),
                sensitive_terms_count = VALUES(sensitive_terms_count),
                suspicious_links_count = VALUES(suspicious_links_count),
                repeated_sharing = VALUES(repeated_sharing),
                high_risk_user = VALUES(high_risk_user),
                calculated_at = CURRENT_TIMESTAMP
        """
        
        cursor.execute(
            score_query,
            (
                message_id,
                score_details["total_score"],
                score_details["sensitive_terms_count"],
                score_details["suspicious_links_count"],
                1 if score_details["repeated_sharing"] else 0,
                1 if score_details["high_risk_user"] else 0,
            ),
        )
        
        conn.commit()
    except mysql.connector.Error as exc:
        logging.error("Database error inserting score: %s", exc)
    finally:
        cursor.close()
        conn.close()


async def insert_data_to_db(message_data: dict, bot_username: str, db_config: dict) -> None:
    """
    Insert message-related data into the database.
    """
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        group_query = "INSERT INTO `group` (group_name) VALUES (%s) ON DUPLICATE KEY UPDATE group_name = VALUES(group_name)"
        user_query = (
            "INSERT INTO `user` (username, name) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE name = VALUES(name)"
        )
        file_query = (
            "INSERT INTO files (file_name, file_type, hash) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE file_name = VALUES(file_name), file_type = VALUES(file_type)"
        )
        content_query = (
            "INSERT INTO content (id_message, date_message, content, translated_content, file_id, id_user, id_group, id_bot) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        link_query = "INSERT INTO links (link, message_id) VALUES (%s, %s)"
        bot_query = "INSERT INTO bot (name) VALUES (%s) ON DUPLICATE KEY UPDATE name = VALUES(name)"

        # Insert or update bot details
        cursor.execute(bot_query, (bot_username,))
        cursor.execute("SELECT id FROM bot WHERE name = %s", (bot_username,))
        result = cursor.fetchone()
        bot_id = result[0] if result else None

        # Insert or update group details
        cursor.execute(group_query, (message_data["group_name"],))
        cursor.execute("SELECT group_id FROM `group` WHERE group_name = %s", (message_data["group_name"],))
        result = cursor.fetchone()
        group_id = result[0] if result else None

        # Insert or update user details
        cursor.execute(user_query, (message_data["sender_username"], message_data["sender"]))
        cursor.execute("SELECT id_user FROM `user` WHERE username = %s", (message_data["sender_username"],))
        result = cursor.fetchone()
        user_id = result[0] if result else None

        # Insert or update file details
        file_id = None
        for attached_file in message_data["attached_files"]:
            file_name = attached_file["file"]
            file_type = attached_file["mime_type"]
            file_hash = attached_file["hash"]
            cursor.execute(file_query, (file_name, file_type, file_hash))
            cursor.execute("SELECT file_id FROM files WHERE hash = %s", (file_hash,))
            result = cursor.fetchone()
            if result:
                file_id = result[0]

        # Insert content details
        cursor.execute(
            content_query,
            (
                message_data["message_id"],
                message_data["date"],
                message_data["content"],
                message_data["translated_content"],
                file_id,
                user_id,
                group_id,
                bot_id,
            ),
        )

        # Insert link details
        for link in message_data["in_message_urls"]:
            cursor.execute(link_query, (link, message_data["message_id"]))

        conn.commit()
    except mysql.connector.Error as exc:
        logging.error("Database error: %s", exc)
    finally:
        cursor.close()
        conn.close()


async def get_random_scored_message(db_config: dict, exclude_reviewed: bool = True) -> dict:
    """
    Search a random scored message from the database.
    
    Args:
        db_config: Database configuration
        exclude_reviewed: If True, exclude messages that have already been reviewed
    
    Returns:
        Dictionary with the message data and its score, or None if there are no messages
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Base query to search scored messages
        if exclude_reviewed:
            query = """
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
            """
        else:
            query = """
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
            """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            # Search links associated with the message
            link_query = "SELECT link FROM links WHERE message_id = %s"
            cursor.execute(link_query, (result['id_message'],))
            links = [row['link'] for row in cursor.fetchall()]
            result['links'] = links
            
            # Check if there is feedback
            feedback_query = "SELECT is_correct, feedback_notes FROM training_feedback WHERE message_id = %s"
            cursor.execute(feedback_query, (result['id_message'],))
            feedback = cursor.fetchone()
            if feedback:
                result['feedback'] = feedback
            else:
                result['feedback'] = None
        
        cursor.close()
        conn.close()
        
        return result
        
    except mysql.connector.Error as exc:
        logging.error(f"Error searching random scored message: {exc}")
        return None


async def save_training_feedback(
    message_id: int,
    original_score: int,
    is_correct: bool,
    db_config: dict,
    feedback_notes: str = None
) -> bool:
    """
    Save training feedback for a message.
    
    Args:
        message_id: ID of the message
        original_score: Original score of the message
        is_correct: True if the score is correct, False otherwise
        db_config: Database configuration
        feedback_notes: Additional notes from the analyst (optional)
    
    Returns:
        True if the feedback was saved successfully, False otherwise
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        query = """
            INSERT INTO training_feedback 
            (message_id, original_score, is_correct, feedback_notes, reviewed_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
                is_correct = VALUES(is_correct),
                feedback_notes = VALUES(feedback_notes),
                reviewed_at = CURRENT_TIMESTAMP
        """
        
        cursor.execute(
            query,
            (
                message_id,
                original_score,
                1 if is_correct else 0,
                feedback_notes
            )
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info(f"Feedback saved for message {message_id}: {'correct' if is_correct else 'incorrect'}")
        return True
        
    except mysql.connector.Error as exc:
        logging.error(f"Error saving feedback: {exc}")
        return False


def get_training_statistics(db_config: dict) -> dict:
    """
    Return statistics about the training system.
    
    Args:
        db_config: Database configuration
    
    Returns:
        Dictionary with training statistics
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Total scored messages
        cursor.execute("SELECT COUNT(*) as total FROM message_scores WHERE score > 0")
        total_scored = cursor.fetchone()['total']
        
        # Reviewed messages
        cursor.execute("SELECT COUNT(*) as total FROM training_feedback WHERE is_correct IS NOT NULL")
        total_reviewed = cursor.fetchone()['total']
        
        # Correct messages
        cursor.execute("SELECT COUNT(*) as total FROM training_feedback WHERE is_correct = 1")
        total_correct = cursor.fetchone()['total']
        
        # Incorrect messages
        cursor.execute("SELECT COUNT(*) as total FROM training_feedback WHERE is_correct = 0")
        total_incorrect = cursor.fetchone()['total']
        
        # Pending messages
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM message_scores ms
            LEFT JOIN training_feedback tf ON ms.message_id = tf.message_id
            WHERE ms.score > 0 AND (tf.id IS NULL OR tf.is_correct IS NULL)
        """)
        total_pending = cursor.fetchone()['total']
        
        accuracy = (total_correct / total_reviewed * 100) if total_reviewed > 0 else 0
        
        cursor.close()
        conn.close()
        
        return {
            'total_scored': total_scored,
            'total_reviewed': total_reviewed,
            'total_correct': total_correct,
            'total_incorrect': total_incorrect,
            'total_pending': total_pending,
            'accuracy': round(accuracy, 2)
        }
        
    except mysql.connector.Error as exc:
        logging.error(f"Error searching statistics: {exc}")
        return {}

