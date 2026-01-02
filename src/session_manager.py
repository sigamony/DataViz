
"""
Session Manager Module - Handles user sessions and conversation memory.
Manages session creation, conversation history, and cleanup using MongoDB.
"""

from datetime import datetime, timedelta
import logging
import uuid
import json
from typing import List, Dict, Optional
from src.database import get_db

MAX_MESSAGES = 10  # Maximum messages to keep in context
SESSION_EXPIRY_HOURS = 24  # Sessions expire after 24 hours

logger = logging.getLogger(__name__)

def init_session_tables():
    """Initialize MongoDB indexes for session management."""
    db = get_db()
    
    # Session ID should be unique
    db.sessions.create_index("session_id", unique=True)
    
    # Automatic expiration (TTL) based on last_active
    # expireAfterSeconds = 24 * 3600
    db.sessions.create_index("last_active", expireAfterSeconds=SESSION_EXPIRY_HOURS * 3600)
    
    logger.info("Session indexes initialized (TTL: 24h).")

def create_session(user_profile: Dict) -> str:
    """
    Create a new session with user profile.
    """
    db = get_db()
    session_id = str(uuid.uuid4())
    
    db.sessions.insert_one({
        "session_id": session_id,
        "user_profile": user_profile,
        "created_at": datetime.utcnow(),
        "last_active": datetime.utcnow(),
        "conversations": {} # Nested dict: file_id -> list of messages
    })
    
    return session_id

def get_session(session_id: str) -> Optional[Dict]:
    """Retrieve session information."""
    db = get_db()
    session = db.sessions.find_one({"session_id": session_id})
    
    if not session:
        return None
    
    # MongoDB TTL handles cleanup, but if we accessed it just before delete:
    return {
        'session_id': session['session_id'],
        'user_profile': session['user_profile'],
        'created_at': session['created_at'],
        'last_active': session['last_active']
    }

def update_session_activity(session_id: str):
    """Update last active timestamp for session."""
    db = get_db()
    db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"last_active": datetime.utcnow()}}
    )

def add_message(session_id: str, file_id: str, role: str, message: str):
    """
    Add a message to conversation history.
    Uses embedded documents for simpler management.
    """
    db = get_db()
    
    new_msg = {
        'role': role,
        'content': message,
        'timestamp': datetime.utcnow()
    }
    
    # Update logic:
    # 1. Push new message to conversations.file_id
    # 2. Slice to keep only last MAX_MESSAGES
    # 3. Update last_active
    
    # Note: Mongo $push with $slice can do this atomically
    
    key = f"conversations.{file_id}"
    
    db.sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {
                key: {
                    "$each": [new_msg],
                    "$slice": -MAX_MESSAGES # Keep last N
                }
            },
            "$set": {"last_active": datetime.utcnow()}
        }
    )

def get_conversation_history(session_id: str, file_id: str, limit: int = MAX_MESSAGES) -> List[Dict]:
    """
    Get recent conversation history for a session and file.
    """
    db = get_db()
    
    # Projection to fetch only specific conversation
    key = f"conversations.{file_id}"
    
    session = db.sessions.find_one(
        {"session_id": session_id},
        {key: 1} # Only return this field
    )
    
    if not session or 'conversations' not in session or file_id not in session['conversations']:
        return []
        
    messages = session['conversations'][file_id]
    
    # Messages are stored in order (oldest -> newest) because of $push
    # API expects them in that order usually, or we can reverse if needed.
    # The SQL impl returned reversed(rows) where rows were ORDER BY timestamp DESC (newest first).
    # So SQL returned [oldest, ..., newest].
    # Our Mongo list is [oldest, ..., newest]. 
    # So we return as is.
    
    return messages

def get_message_count(session_id: str, file_id: str) -> int:
    """Get total message count for a session and file."""
    db = get_db()
    key = f"conversations.{file_id}"
    
    session = db.sessions.find_one(
        {"session_id": session_id},
        {key: 1}
    )
    
    if not session or 'conversations' not in session or file_id not in session['conversations']:
        return 0
        
    return len(session['conversations'][file_id])

def clear_conversation(session_id: str, file_id: str):
    """Clear all conversation history for a specific file."""
    db = get_db()
    key = f"conversations.{file_id}"
    
    db.sessions.update_one(
        {"session_id": session_id},
        {"$unset": {key: ""}}
    )

def cleanup_expired_sessions():
    """
    Manual cleanup is largely handled by MongoDB TTL indexes.
    However, we can keep this for logging purposes or forced cleanup.
    Returns number of sessions removed (approx).
    """
    # Expiry is handled by MongoDB TTL on last_active
    return 0
