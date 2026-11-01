"""
Module: auth.py
Handles user authentication, password hashing, verification, and session state.

Features:
- Secure password hashing using bcrypt with salt (or SHA-256 PBKDF2 fallback)
- User storage in SQLite `users` table
- Session verification helpers for Streamlit
"""

import os
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from src.database import BatteryDatabase

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False


def hash_password(password: str) -> str:
    """Hash password securely using bcrypt or PBKDF2 fallback."""
    if HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    else:
        # Fallback to PBKDF2-HMAC-SHA256
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return f"pbkdf2${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify plain password against stored hash."""
    if not stored_hash or not plain_password:
        return False

    if stored_hash.startswith("pbkdf2$"):
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False
        salt = bytes.fromhex(parts[1])
        expected_key = parts[2]
        test_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000).hex()
        return test_key == expected_key

    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False

    return False


class AuthManager:
    def __init__(self, db: BatteryDatabase):
        self.db = db
        self.ensure_default_admin()

    def ensure_default_admin(self):
        """Ensures at least one administrator account exists, using .env or safe default."""
        admin_user = os.getenv("ADMIN_USERNAME", "admin")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (admin_user,))
            if not cursor.fetchone():
                pw_hash = hash_password(admin_pass)
                now_utc = datetime.now(timezone.utc).isoformat()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, created_at)
                    VALUES (?, ?, 'administrator', ?)
                """, (admin_user, pw_hash, now_utc))
                conn.commit()

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verify credentials and return user profile if valid."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username.strip(),))
            row = cursor.fetchone()
            if not row:
                return False, None

            stored_hash = row["password_hash"]
            if verify_password(password, stored_hash):
                user_info = {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"]
                }
                return True, user_info

        return False, None

    def register_user(self, username: str, password: str, role: str = "operator") -> Tuple[bool, str]:
        """Registers a new user account."""
        username = username.strip()
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, f"Username '{username}' already exists."

            pw_hash = hash_password(password)
            now_utc = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?)
            """, (username, pw_hash, role, now_utc))
            conn.commit()
            return True, f"User '{username}' registered successfully."
