import logging
import mysql.connector


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

