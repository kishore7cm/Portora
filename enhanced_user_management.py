"""
Enhanced User Management System
Handles user registration, authentication, profile management, portfolios, and bots
"""

import sqlite3
import hashlib
import jwt
import datetime
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
import logging
import json

logger = logging.getLogger(__name__)

class EnhancedUserManager:
    def __init__(self, db_path: str = "enhanced_users.db"):
        self.db_path = db_path
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the enhanced database with multiple tables"""
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
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    preferences TEXT DEFAULT '{}'
                )
            ''')
            
            # Create portfolios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_primary BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Create portfolio_holdings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    purchase_price REAL,
                    current_price REAL,
                    asset_class TEXT,
                    sector TEXT,
                    beta REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios (id) ON DELETE CASCADE
                )
            ''')
            
            # Create bots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    bot_type TEXT NOT NULL,
                    status TEXT DEFAULT 'inactive',
                    config TEXT DEFAULT '{}',
                    performance_data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_run TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Create bot_trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id INTEGER NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (bot_id) REFERENCES bots (id) ON DELETE CASCADE
                )
            ''')
            
            # Create user_sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    priority TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Enhanced database initialized successfully with multiple tables")
            
        except Exception as e:
            logger.error(f"Error initializing enhanced database: {e}")
            raise

    def register_user(self, email: str, password: str, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return {"success": False, "message": "User already exists"}
            
            # Hash password
            password_hash = self.pwd_context.hash(password)
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name))
            
            user_id = cursor.lastrowid
            
            # Create default portfolio
            cursor.execute('''
                INSERT INTO portfolios (user_id, name, description, is_primary)
                VALUES (?, ?, ?, ?)
            ''', (user_id, "Main Portfolio", "Default portfolio", 1))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "user_id": user_id, "message": "User registered successfully"}
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return {"success": False, "message": f"Registration failed: {str(e)}"}

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return user info"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, password_hash, first_name, last_name, is_active
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return {"success": False, "message": "User not found"}
            
            user_id, email, password_hash, first_name, last_name, is_active = user
            
            if not is_active:
                return {"success": False, "message": "Account is inactive"}
            
            if not self.pwd_context.verify(password, password_hash):
                return {"success": False, "message": "Invalid password"}
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"success": False, "message": f"Authentication failed: {str(e)}"}

    def create_portfolio(self, user_id: int, name: str, description: str = "") -> int:
        """Create a new portfolio for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO portfolios (user_id, name, description, is_primary, created_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (user_id, name, description, False))
            
            portfolio_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created portfolio '{name}' for user {user_id}")
            return portfolio_id
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            return None

    def add_holding_to_portfolio(self, portfolio_id: int, symbol: str, quantity: float, 
                                asset_class: str, sector: str, purchase_price: float = 0.0, 
                                current_price: float = 0.0, beta: float = 1.0) -> bool:
        """Add a holding to a portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO portfolio_holdings 
                (portfolio_id, symbol, quantity, purchase_price, current_price, asset_class, sector, beta, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (portfolio_id, symbol, quantity, purchase_price, current_price, asset_class, sector, beta))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added holding {symbol} to portfolio {portfolio_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding holding to portfolio: {e}")
            return False

    def get_user_portfolios(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all portfolios for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, is_primary, created_at, updated_at
                FROM portfolios WHERE user_id = ? ORDER BY is_primary DESC, created_at ASC
            ''', (user_id,))
            
            portfolios = []
            for row in cursor.fetchall():
                portfolios.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "is_primary": bool(row[3]),
                    "created_at": row[4],
                    "updated_at": row[5]
                })
            
            conn.close()
            return portfolios
            
        except Exception as e:
            logger.error(f"Error getting user portfolios: {e}")
            return []

    def get_portfolio_holdings(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """Get all holdings for a portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT symbol, quantity, purchase_price, current_price, asset_class, sector, beta
                FROM portfolio_holdings WHERE portfolio_id = ? ORDER BY symbol
            ''', (portfolio_id,))
            
            holdings = []
            for row in cursor.fetchall():
                holdings.append({
                    "symbol": row[0],
                    "quantity": row[1],
                    "purchase_price": row[2],
                    "current_price": row[3],
                    "asset_class": row[4],
                    "sector": row[5],
                    "beta": row[6]
                })
            
            conn.close()
            return holdings
            
        except Exception as e:
            logger.error(f"Error getting portfolio holdings: {e}")
            return []

    def get_primary_portfolio_id(self, user_id: int) -> Optional[int]:
        """Return the user's primary portfolio id, or None if not found"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT id FROM portfolios WHERE user_id = ? AND is_primary = 1 ORDER BY created_at ASC LIMIT 1''',
                (user_id,)
            )
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting primary portfolio id: {e}")
            return None

    def clear_portfolio_holdings(self, portfolio_id: int) -> bool:
        """Delete all holdings for a portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM portfolio_holdings WHERE portfolio_id = ?', (portfolio_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error clearing portfolio holdings: {e}")
            return False

    def create_bot(self, user_id: int, name: str, bot_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new trading bot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            config_json = json.dumps(config or {})
            
            cursor.execute('''
                INSERT INTO bots (user_id, name, bot_type, config)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, bot_type, config_json))
            
            bot_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {"success": True, "bot_id": bot_id, "message": "Bot created successfully"}
            
        except Exception as e:
            logger.error(f"Error creating bot: {e}")
            return {"success": False, "message": f"Bot creation failed: {str(e)}"}

    def get_user_bots(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all bots for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, bot_type, status, config, performance_data, created_at, last_run
                FROM bots WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            
            bots = []
            for row in cursor.fetchall():
                bots.append({
                    "id": row[0],
                    "name": row[1],
                    "bot_type": row[2],
                    "status": row[3],
                    "config": json.loads(row[4]) if row[4] else {},
                    "performance_data": json.loads(row[5]) if row[5] else {},
                    "created_at": row[6],
                    "last_run": row[7]
                })
            
            conn.close()
            return bots
            
        except Exception as e:
            logger.error(f"Error getting user bots: {e}")
            return []

    def update_bot_status(self, bot_id: int, status: str) -> Dict[str, Any]:
        """Update bot status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE bots SET status = ?, last_run = CURRENT_TIMESTAMP WHERE id = ?
            ''', (status, bot_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Bot status updated"}
            
        except Exception as e:
            logger.error(f"Error updating bot status: {e}")
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def add_bot_trade(self, bot_id: int, symbol: str, action: str, quantity: float, price: float) -> Dict[str, Any]:
        """Add a trade executed by a bot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bot_trades (bot_id, symbol, action, quantity, price)
                VALUES (?, ?, ?, ?, ?)
            ''', (bot_id, symbol, action, quantity, price))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Trade recorded"}
            
        except Exception as e:
            logger.error(f"Error adding bot trade: {e}")
            return {"success": False, "message": f"Trade recording failed: {str(e)}"}

    def get_bot_trades(self, bot_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades for a bot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT symbol, action, quantity, price, timestamp, status
                FROM bot_trades WHERE bot_id = ? ORDER BY timestamp DESC LIMIT ?
            ''', (bot_id, limit))
            
            trades = []
            for row in cursor.fetchall():
                trades.append({
                    "symbol": row[0],
                    "action": row[1],
                    "quantity": row[2],
                    "price": row[3],
                    "timestamp": row[4],
                    "status": row[5]
                })
            
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Error getting bot trades: {e}")
            return []

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, first_name, last_name, is_active, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    "id": user[0],
                    "email": user[1],
                    "first_name": user[2],
                    "last_name": user[3],
                    "is_active": bool(user[4]),
                    "created_at": user[5],
                    "last_login": user[6]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            preferences_json = json.dumps(preferences)
            cursor.execute('''
                UPDATE users SET preferences = ? WHERE id = ?
            ''', (preferences_json, user_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Preferences updated"}
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preferences FROM users WHERE id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                prefs = json.loads(result[0])
                # Ensure has_seen_onboarding exists with default False
                if 'has_seen_onboarding' not in prefs:
                    prefs['has_seen_onboarding'] = False
                return prefs
            return {'has_seen_onboarding': False}
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {'has_seen_onboarding': False}

    def mark_onboarding_complete(self, user_id: int) -> Dict[str, Any]:
        """Mark onboarding as complete for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current preferences
            cursor.execute('SELECT preferences FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result and result[0]:
                prefs = json.loads(result[0])
            else:
                prefs = {}
            
            # Update onboarding status
            prefs['has_seen_onboarding'] = True
            prefs['onboarding_completed_at'] = datetime.datetime.now().isoformat()
            
            # Save updated preferences
            preferences_json = json.dumps(prefs)
            cursor.execute('''
                UPDATE users SET preferences = ? WHERE id = ?
            ''', (preferences_json, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Onboarding marked complete for user {user_id}")
            return {"success": True, "message": "Onboarding completed"}
            
        except Exception as e:
            logger.error(f"Error marking onboarding complete: {e}")
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def create_alert(self, user_id: int, alert_type: str, title: str, message: str, 
                    priority: str = 'medium', expires_at: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new alert for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute('''
                INSERT INTO alerts (user_id, type, title, message, priority, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, alert_type, title, message, priority, expires_at, metadata_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Alert created for user {user_id}: {title}")
            return {"success": True, "message": "Alert created successfully"}
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return {"success": False, "message": f"Alert creation failed: {str(e)}"}

    def get_user_alerts(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alerts for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT id, type, title, message, is_read, priority, created_at, expires_at, metadata
                FROM alerts 
                WHERE user_id = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
            '''
            params = [user_id]
            
            if unread_only:
                query += ' AND is_read = 0'
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "message": row[3],
                    "is_read": bool(row[4]),
                    "priority": row[5],
                    "created_at": row[6],
                    "expires_at": row[7],
                    "metadata": json.loads(row[8]) if row[8] else {}
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []

    def mark_alert_read(self, alert_id: int, user_id: int) -> Dict[str, Any]:
        """Mark an alert as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts SET is_read = 1 
                WHERE id = ? AND user_id = ?
            ''', (alert_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Alert marked as read"}
            
        except Exception as e:
            logger.error(f"Error marking alert as read: {e}")
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def mark_all_alerts_read(self, user_id: int) -> Dict[str, Any]:
        """Mark all alerts as read for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts SET is_read = 1 
                WHERE user_id = ? AND is_read = 0
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "All alerts marked as read"}
            
        except Exception as e:
            logger.error(f"Error marking all alerts as read: {e}")
            return {"success": False, "message": f"Update failed: {str(e)}"}

    def get_unread_alert_count(self, user_id: int) -> int:
        """Get count of unread alerts for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE user_id = ? AND is_read = 0 
                AND (expires_at IS NULL OR expires_at > datetime('now'))
            ''', (user_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting unread alert count: {e}")
            return 0

# Initialize enhanced user manager
enhanced_user_manager = EnhancedUserManager()
