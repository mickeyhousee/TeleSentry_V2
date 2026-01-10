"""
Message scoring system using rules + light ML.
Calculates a risk score for each message based on:
- Sensitive terms: +3 (adjustable via training)
- Links to suspicious sites: +4 (adjustable via training)
- Repeated sharing: +2 (adjustable via training)
- Correlation with high-risk users: +5 (adjustable via training)
"""
import logging
import re
from typing import Dict, List, Set, Optional
from collections import Counter
import mysql.connector


# List of sensitive terms (can be expanded)
SENSITIVE_TERMS = [
    # Portuguese
    "phishing", "scam", "fraude", "golpe", "hack", "malware", "vírus",
    "bitcoin", "criptomoeda", "investimento garantido", "ganhe dinheiro rápido",
    "clique aqui", "urgente", "sua conta foi bloqueada", "verifique sua conta",
    "senha expirada", "atualize seus dados", "oferta exclusiva", "prêmio",
    # English
    "password expired", "account blocked", "verify account", "click here",
    "urgent", "exclusive offer", "prize", "guaranteed investment",
    "make money fast", "cryptocurrency", "virus", "malware", "hack",
    "fraud", "scam", "phishing"
]

# List of suspicious domains (can be expanded)
SUSPICIOUS_DOMAINS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "short.link",
    "rebrand.ly", "cutt.ly", "is.gd", "v.gd", "shorte.st", "adf.ly",
    "bc.vc", "ouo.io", "linkbucks.com", "adfly.com"
]

# Suspicious URL patterns
SUSPICIOUS_URL_PATTERNS = [
    r"bit\.ly",
    r"tinyurl\.com",
    r"t\.co",
    r"goo\.gl",
    r"short\.link",
    r"rebrand\.ly",
    r"cutt\.ly",
]

# Default weights (will be automatically adjusted based on feedback)
DEFAULT_WEIGHTS = {
    "sensitive_terms": 3.0,
    "suspicious_links": 4.0,
    "repeated_sharing": 2.0,
    "high_risk_user": 5.0
}


def detect_sensitive_terms(content: str, translated_content: str = "") -> int:
    """
    Detects sensitive terms in the message content.
    Returns the number of terms found.
    """
    if not content and not translated_content:
        return 0
    
    text_to_check = f"{content} {translated_content}".lower()
    found_terms = 0
    
    for term in SENSITIVE_TERMS:
        if term.lower() in text_to_check:
            found_terms += 1
            logging.debug(f"Sensitive term detected: {term}")
    
    return found_terms


def detect_suspicious_links(urls: List[str]) -> int:
    """
    Detects links to suspicious sites.
    Returns the number of suspicious links found.
    """
    if not urls:
        return 0
    
    suspicious_count = 0
    
    for url in urls:
        url_lower = url.lower()
        # Check suspicious domains
        for domain in SUSPICIOUS_DOMAINS:
            if domain in url_lower:
                suspicious_count += 1
                logging.debug(f"Suspicious link detected: {url}")
                break
        # Check suspicious patterns
        if not suspicious_count:
            for pattern in SUSPICIOUS_URL_PATTERNS:
                if re.search(pattern, url_lower):
                    suspicious_count += 1
                    logging.debug(f"Suspicious pattern detected in: {url}")
                    break
    
    return suspicious_count


def detect_repeated_sharing(content: str, db_config: dict, message_id: int = None) -> bool:
    """
    Detects if the content has been shared repeatedly.
    Returns True if the content (or similar) was found in other messages.
    """
    if not content or len(content.strip()) < 10:  # Ignore very short messages
        return False
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Normalize content for comparison (remove extra spaces, convert to lowercase)
        normalized_content = re.sub(r'\s+', ' ', content.strip().lower())
        
        # Search for messages with similar content (using LIKE for basic similarity)
        # Get first 50 characters for comparison
        search_pattern = normalized_content[:50] + "%"
        
        if message_id:
            query = """
                SELECT COUNT(*) FROM content 
                WHERE id_message != %s 
                AND (content LIKE %s OR translated_content LIKE %s)
                LIMIT 5
            """
            cursor.execute(query, (message_id, search_pattern, search_pattern))
        else:
            query = """
                SELECT COUNT(*) FROM content 
                WHERE (content LIKE %s OR translated_content LIKE %s)
                LIMIT 5
            """
            cursor.execute(query, (search_pattern, search_pattern))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        # If found at least 2 similar messages, consider it repeated
        is_repeated = count >= 2
        if is_repeated:
            logging.debug(f"Repeated sharing detected for message {message_id or 'new'}")
        
        return is_repeated
        
    except Exception as exc:
        logging.error(f"Error checking repeated sharing: {exc}")
        return False


def get_high_risk_users(db_config: dict) -> Set[int]:
    """
    Identifies high-risk users based on history.
    A user is considered high-risk if:
    - Sent messages with many suspicious links
    - Sent messages with sensitive terms repeatedly
    - Has a history of flagged messages
    
    Returns a set with the IDs of high-risk users.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Search for users who have messages with suspicious links
        query_links = """
            SELECT DISTINCT c.id_user 
            FROM content c
            INNER JOIN links l ON c.id_message = l.message_id
            WHERE l.link LIKE '%bit.ly%' 
               OR l.link LIKE '%tinyurl%'
               OR l.link LIKE '%t.co%'
               OR l.link LIKE '%goo.gl%'
               OR l.link LIKE '%short.link%'
            GROUP BY c.id_user
            HAVING COUNT(DISTINCT c.id_message) >= 2
        """
        
        cursor.execute(query_links)
        high_risk_user_ids = {row[0] for row in cursor.fetchall() if row[0] is not None}
        
        # Search for users with many messages (possible spam)
        query_volume = """
            SELECT id_user, COUNT(*) as msg_count
            FROM content
            WHERE id_user IS NOT NULL
            GROUP BY id_user
            HAVING msg_count >= 10
        """
        
        cursor.execute(query_volume)
        volume_users = {row[0] for row in cursor.fetchall() if row[0] is not None}
        
        # Combine both criteria
        high_risk_user_ids.update(volume_users)
        
        cursor.close()
        conn.close()
        
        logging.debug(f"High-risk users identified: {len(high_risk_user_ids)}")
        return high_risk_user_ids
        
    except Exception as exc:
        logging.error(f"Error identifying high-risk users: {exc}")
        return set()


def get_adjusted_weights(db_config: dict) -> Dict[str, float]:
    """
    Calcula pesos ajustados baseado no feedback de treinamento.
    Analisa mensagens revisadas e ajusta os pesos para melhorar a precisão.
    
    Args:
        db_config: Configuração do banco de dados
    
    Returns:
        Dict com pesos ajustados para cada fator
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Search training feedback with message details
        query = """
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
        """
        
        cursor.execute(query)
        feedbacks = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if len(feedbacks) < 10:  # Need at least 10 feedbacks to adjust
            logging.debug("Few feedbacks available, using default weights")
            return DEFAULT_WEIGHTS.copy()
        
        # Analyze feedbacks to adjust weights
        # Strategy: If many messages with a specific factor were marked as incorrect,
        # we reduce the weight of that factor. If marked as correct, we maintain or increase.
        
        weights = DEFAULT_WEIGHTS.copy()
        
        # Analyze each factor
        factors = {
            "sensitive_terms": "sensitive_terms_count",
            "suspicious_links": "suspicious_links_count",
            "repeated_sharing": "repeated_sharing",
            "high_risk_user": "high_risk_user"
        }
        
        for factor_name, db_field in factors.items():
            correct_with_factor = 0
            incorrect_with_factor = 0
            total_with_factor = 0
            
            for feedback in feedbacks:
                has_factor = False
                if db_field == "sensitive_terms_count":
                    has_factor = feedback[db_field] > 0
                elif db_field == "suspicious_links_count":
                    has_factor = feedback[db_field] > 0
                elif db_field == "repeated_sharing":
                    has_factor = feedback[db_field] == 1
                elif db_field == "high_risk_user":
                    has_factor = feedback[db_field] == 1
                
                if has_factor:
                    total_with_factor += 1
                    if feedback["is_correct"] == 1:
                        correct_with_factor += 1
                    else:
                        incorrect_with_factor += 1
            
            if total_with_factor > 0:
                accuracy = correct_with_factor / total_with_factor
                # If accuracy is low (< 0.6), reduce weight
                # If high (> 0.8), maintain or slightly increase
                if accuracy < 0.6:
                    # Reduce weight by up to 30%
                    adjustment = 1.0 - (0.6 - accuracy) * 0.5
                    weights[factor_name] = max(DEFAULT_WEIGHTS[factor_name] * 0.5, 
                                               DEFAULT_WEIGHTS[factor_name] * adjustment)
                    logging.info(f"Adjusting weight of {factor_name}: {DEFAULT_WEIGHTS[factor_name]:.2f} -> {weights[factor_name]:.2f} (accuracy: {accuracy:.2%})")
                elif accuracy > 0.85:
                    # Slightly increase if very accurate
                    weights[factor_name] = DEFAULT_WEIGHTS[factor_name] * 1.1
                    logging.debug(f"Increasing weight of {factor_name} due to high accuracy: {accuracy:.2%}")
        
        return weights
        
    except Exception as exc:
        logging.error(f"Error calculating adjusted weights: {exc}")
        return DEFAULT_WEIGHTS.copy()


def calculate_message_score(
    message_data: Dict,
    db_config: dict,
    high_risk_users: Set[int] = None,
    use_training_weights: bool = True
) -> Dict:
    """
    Calculates the risk score for a message.
    Uses automatically adjusted weights based on training feedback.
    
    Args:
        message_data: Message data
        db_config: Database configuration
        high_risk_users: Set of high-risk user IDs (optional, will be fetched if not provided)
        use_training_weights: If True, uses adjusted weights based on training
    
    Returns:
        Dict with total score and factor details
    """
    # Get adjusted weights if enabled
    if use_training_weights:
        weights = get_adjusted_weights(db_config)
    else:
        weights = DEFAULT_WEIGHTS.copy()
    
    score = 0
    score_details = {
        "sensitive_terms_count": 0,
        "suspicious_links_count": 0,
        "repeated_sharing": False,
        "high_risk_user": False,
        "total_score": 0,
        "weights_used": weights.copy() if use_training_weights else None
    }
    
    # 1. Sensitive terms
    content = message_data.get("content", "")
    translated_content = message_data.get("translated_content", "")
    sensitive_terms_count = detect_sensitive_terms(content, translated_content)
    if sensitive_terms_count > 0:
        score += sensitive_terms_count * weights["sensitive_terms"]
        score_details["sensitive_terms_count"] = sensitive_terms_count
    
    # 2. Suspicious links
    urls = message_data.get("in_message_urls", [])
    suspicious_links_count = detect_suspicious_links(urls)
    if suspicious_links_count > 0:
        score += suspicious_links_count * weights["suspicious_links"]
        score_details["suspicious_links_count"] = suspicious_links_count
    
    # 3. Repeated sharing
    message_id = message_data.get("message_id")
    if message_id and detect_repeated_sharing(content, db_config, message_id):
        score += weights["repeated_sharing"]
        score_details["repeated_sharing"] = True
    
    # 4. Correlation with high-risk users
    if high_risk_users is None:
        high_risk_users = get_high_risk_users(db_config)
    
    # We need to get the user_id from the database
    sender_username = message_data.get("sender_username")
    if sender_username and sender_username != "Unknown":
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT id_user FROM `user` WHERE username = %s", (sender_username,))
            result = cursor.fetchone()
            user_id = result[0] if result else None
            cursor.close()
            conn.close()
            
            if user_id and user_id in high_risk_users:
                score += weights["high_risk_user"]
                score_details["high_risk_user"] = True
        except Exception as exc:
            logging.error(f"Error checking high-risk user: {exc}")
    
    score_details["total_score"] = round(score, 2)
    
    return score_details


def get_message_ranking(db_config: dict, limit: int = 50) -> List[Dict]:
    """
    Generates a ranking of messages that deserve attention, ordered by score.
    
    Args:
        db_config: Database configuration
        limit: Maximum number of messages to return
    
    Returns:
        List of messages ordered by score (highest first)
    """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Search messages with their complete data
        query = """
            SELECT 
                c.id_message,
                c.date_message,
                c.content,
                c.translated_content,
                u.username as sender_username,
                u.name as sender_name,
                g.group_name,
                COALESCE(ms.score, 0) as score,
                ms.sensitive_terms_count,
                ms.suspicious_links_count,
                ms.repeated_sharing,
                ms.high_risk_user
            FROM content c
            LEFT JOIN `user` u ON c.id_user = u.id_user
            LEFT JOIN `group` g ON c.id_group = g.group_id
            LEFT JOIN message_scores ms ON c.id_message = ms.message_id
            WHERE COALESCE(ms.score, 0) > 0
            ORDER BY COALESCE(ms.score, 0) DESC, c.date_message DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return results
        
    except mysql.connector.Error as exc:
        logging.error(f"Error generating message ranking: {exc}")
        return []

