import sqlite3
import json
import os

DB_PATH = "chart_visualizer.db"

def init_db():
    """Initialize the database with the required table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT,
            filepath TEXT,
            profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_file_metadata(file_id, filename, filepath, profile):
    """Save file metadata to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Serialize profile dict to JSON string
    profile_json = json.dumps(profile, default=str)
    
    cursor.execute('''
        INSERT INTO files (id, filename, filepath, profile)
        VALUES (?, ?, ?, ?)
    ''', (file_id, filename, filepath, profile_json))
    
    conn.commit()
    conn.close()

def get_file_metadata(file_id):
    """Retrieve file metadata from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT filepath, profile, filename FROM files WHERE id = ?', (file_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        filepath, profile_json, filename = row
        # Deserialize JSON string back to dict
        profile = json.loads(profile_json)
        return {
            "path": filepath,
            "profile": profile,
            "filename": filename
        }
    return None
