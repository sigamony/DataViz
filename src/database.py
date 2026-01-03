
import os
import pymongo
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

# Global client to be reused
_mongo_client = None
_db = None

def get_db_client():
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/chart_visualizer")
        try:
            _mongo_client = MongoClient(mongo_uri)
            # Send a ping to confirm a successful connection
            _mongo_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e
    return _mongo_client

def get_db():
    global _db
    if _db is None:
        client = get_db_client()
        # Parse database name from URI or default to 'chart_visualizer'
        # Default pymongo behavior uses the db in URI if present
        try:
            _db = client.get_database()
        except pymongo.errors.ConfigurationError:
            _db = client.get_database("chart_visualizer") 
    return _db

def init_db():
    """Initialize the database (create indexes if needed)."""
    db = get_db()
    # Create indexes for files
    db.files.create_index("id", unique=True)
    logger.info("MongoDB initialized and indexes verified.")

def save_file_metadata(file_id, filename, filepath, profile):
    """Save file metadata to the database."""
    db = get_db()
    db.files.insert_one({
        "id": file_id,
        "filename": filename,
        "filepath": filepath,
        "profile": profile,
        "created_at": datetime.utcnow()
    })

def get_file_metadata(file_id):
    """Retrieve file metadata from the database."""
    db = get_db()
    doc = db.files.find_one({"id": file_id})
    if doc:
        return {
            "path": doc["filepath"],
            "profile": doc["profile"],
            "filename": doc["filename"]
        }
    return None

from datetime import datetime
