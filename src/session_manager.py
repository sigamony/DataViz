"""
Session Manager Module - Handles user sessions and conversation memory.
Manages session creation, conversation history, and cleanup.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

DB_PATH = "chart_visualizer.db"
MAX_MESSAGES = 10  # Maximum messages to keep in context
SESSION_EXPIRY_HOURS = 24  # Sessions expire after 24 hours


def init_session_tables():
    """Initialize database tables for session management."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Conversation history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            file_id TEXT,
            role TEXT,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    ''')
    
    # Index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_session_timestamp 
        ON conversations(session_id, timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()


def create_session(user_profile: Dict) -> str:
    """
    Create a new session with user profile.
    
    Args:
        user_profile: Dictionary containing username and avatar
        
    Returns:
        str: Generated session ID
    """
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (session_id, user_profile)
        VALUES (?, ?)
    ''', (session_id, json.dumps(user_profile)))
    
    conn.commit()
    conn.close()
    
    return session_id


def get_session(session_id: str) -> Optional[Dict]:
    """
    Retrieve session information.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dict with session info or None if not found/expired
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_profile, created_at, last_active 
        FROM sessions 
        WHERE session_id = ?
    ''', (session_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    user_profile, created_at, last_active = row
    
    # Check if session expired
    last_active_dt = datetime.fromisoformat(last_active)
    if datetime.now() - last_active_dt > timedelta(hours=SESSION_EXPIRY_HOURS):
        return None
    
    return {
        'session_id': session_id,
        'user_profile': json.loads(user_profile),
        'created_at': created_at,
        'last_active': last_active
    }


def update_session_activity(session_id: str):
    """Update last active timestamp for session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE sessions 
        SET last_active = CURRENT_TIMESTAMP 
        WHERE session_id = ?
    ''', (session_id,))
    
    conn.commit()
    conn.close()


def add_message(session_id: str, file_id: str, role: str, message: str):
    """
    Add a message to conversation history.
    
    Args:
        session_id: Session identifier
        file_id: Associated file ID
        role: 'user' or 'assistant'
        message: Message content
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (session_id, file_id, role, message)
        VALUES (?, ?, ?, ?)
    ''', (session_id, file_id, role, message))
    
    conn.commit()
    conn.close()
    
    # Update session activity
    update_session_activity(session_id)
    
    # Cleanup old messages beyond MAX_MESSAGES
    cleanup_old_messages(session_id, file_id)


def get_conversation_history(session_id: str, file_id: str, limit: int = MAX_MESSAGES) -> List[Dict]:
    """
    Get recent conversation history for a session and file.
    
    Args:
        session_id: Session identifier
        file_id: File identifier
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of message dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, message, timestamp 
        FROM conversations 
        WHERE session_id = ? AND file_id = ?
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (session_id, file_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse to get chronological order
    messages = [
        {
            'role': row[0],
            'content': row[1],
            'timestamp': row[2]
        }
        for row in reversed(rows)
    ]
    
    return messages


def cleanup_old_messages(session_id: str, file_id: str):
    """Remove messages beyond MAX_MESSAGES limit."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM conversations 
        WHERE id IN (
            SELECT id FROM conversations 
            WHERE session_id = ? AND file_id = ?
            ORDER BY timestamp DESC 
            LIMIT -1 OFFSET ?
        )
    ''', (session_id, file_id, MAX_MESSAGES))
    
    conn.commit()
    conn.close()


def cleanup_expired_sessions():
    """Remove expired sessions and their conversations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    expiry_time = datetime.now() - timedelta(hours=SESSION_EXPIRY_HOURS)
    
    # Get expired session IDs
    cursor.execute('''
        SELECT session_id FROM sessions 
        WHERE last_active < ?
    ''', (expiry_time.isoformat(),))
    
    expired_sessions = [row[0] for row in cursor.fetchall()]
    
    if expired_sessions:
        # Delete conversations
        cursor.execute(f'''
            DELETE FROM conversations 
            WHERE session_id IN ({','.join(['?']*len(expired_sessions))})
        ''', expired_sessions)
        
        # Delete sessions
        cursor.execute(f'''
            DELETE FROM sessions 
            WHERE session_id IN ({','.join(['?']*len(expired_sessions))})
        ''', expired_sessions)
        
        conn.commit()
    
    conn.close()
    return len(expired_sessions)


def get_message_count(session_id: str, file_id: str) -> int:
    """Get total message count for a session and file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM conversations 
        WHERE session_id = ? AND file_id = ?
    ''', (session_id, file_id))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count


def clear_conversation(session_id: str, file_id: str):
    """Clear all conversation history for a specific file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM conversations 
        WHERE session_id = ? AND file_id = ?
    ''', (session_id, file_id))
    
    conn.commit()
    conn.close()
