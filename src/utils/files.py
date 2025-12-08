import hashlib
import logging
from typing import Optional


def calculate_file_hash(file_path: str) -> Optional[str]:
    """
    Calculate the SHA-256 hash of a file for integrity and uniqueness.
    """
    hash_algo = hashlib.sha256()
    try:
        with open(file_path, "rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(4096), b""):
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    except Exception as exc:  # pragma: no cover - defensive logging
        logging.error("Error calculating hash: %s", exc)
        return None

