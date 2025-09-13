"""
User Management System
Handles user registration, authentication, and profile management
"""

import sqlite3
import hashlib
import jwt
import datetime
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the users database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    profile_data TEXT  -- JSON string for additional user data
                )
            ''')
            
            # Create user preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER,
                    preference_key TEXT,
                    preference_value TEXT,
                    PRIMARY KEY (user_id, preference_key),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("User database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing user database: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def register_user(self, email: str, password: str, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"success": False, "message": "User already exists"}
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"User registered successfully: {email}")
            return {
                "success": True, 
                "message": "User registered successfully",
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, password_hash, first_name, last_name, is_active
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, email, password_hash, first_name, last_name, is_active = user
            
            if not is_active:
                return None
            
            if not self.verify_password(password, password_hash):
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, first_name, last_name, created_at, last_login, is_active
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, email, first_name, last_name, created_at, last_login, is_active = user
            
            return {
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "created_at": created_at,
                "last_login": last_login,
                "is_active": bool(is_active)
            }
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """Update user profile data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update query
            allowed_fields = ['first_name', 'last_name', 'email']
            updates = []
            values = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            if not updates:
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            
            logger.info(f"User profile updated: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    def set_user_preference(self, user_id: int, key: str, value: str) -> bool:
        """Set a user preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value)
                VALUES (?, ?, ?)
            ''', (user_id, key, value))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error setting user preference: {e}")
            return False
    
    def get_user_preference(self, user_id: int, key: str) -> Optional[str]:
        """Get a user preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preference_value FROM user_preferences 
                WHERE user_id = ? AND preference_key = ?
            ''', (user_id, key))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting user preference: {e}")
            return None
    
    def get_all_user_preferences(self, user_id: int) -> Dict[str, str]:
        """Get all user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preference_key, preference_value FROM user_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return {key: value for key, value in results}
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

# Global user manager instance
user_manager = UserManager()
