from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import shutil
import os
import uuid
import logging

# Import our modules
from src.dataloader import load_data, generate_profile
from src.brain import generate_visualization
from src.executor import execute_chart_code
from src.database import init_db, save_file_metadata, get_file_metadata
from src.demo_data import initialize_demo_datasets, get_demo_datasets, get_demo_dataset_path
from src.session_manager import (
    init_session_tables, create_session, get_session, add_message,
    get_conversation_history, cleanup_expired_sessions, get_message_count, clear_conversation
)
from src.user_profile import generate_user_profile, get_avatar_style
from src.suggestions import generate_suggestions

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Chart Visualizer API")

# Initialize Database and session tables on startup
init_db()
init_session_tables()

# Initialize demo datasets on startup
try:
    initialize_demo_datasets()
    logger.info("Demo datasets initialized successfully")
except Exception as e:
    logger.warning(f"Failed to initialize demo datasets: {e}")

# Cleanup expired sessions on startup
try:
    cleaned = cleanup_expired_sessions()
    logger.info(f"Cleaned up {cleaned} expired sessions")
except Exception as e:
    logger.warning(f"Failed to cleanup sessions: {e}")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



class QueryRequest(BaseModel):
    file_id: str
    query: str
    session_id: Optional[str] = None
    provider: str = "gemini"
    model: str = "gemini-2.5-flash-lite"

from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse('index.html')

@app.get("/health")
def health_check():
    """Lightweight health check endpoint for cron job pings."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/api/session/create")
def create_user_session():
    """
    Create a new anonymous user session with profile.
    """
    try:
        user_profile = generate_user_profile()
        session_id = create_session(user_profile)
        
        return {
            "success": True,
            "session_id": session_id,
            "user_profile": user_profile,
            "avatar_style": get_avatar_style(user_profile['avatar'])
        }
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
def get_user_session(session_id: str):
    """
    Retrieve session information.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "success": True,
        "session": session,
        "avatar_style": get_avatar_style(session['user_profile']['avatar'])
    }

@app.post("/api/conversation/clear")
def clear_conversation_history(session_id: str = Body(...), file_id: str = Body(...)):
    """
    Clear conversation history for a specific file.
    """
    try:
        clear_conversation(session_id, file_id)
        return {"success": True, "message": "Conversation cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo-datasets")
def list_demo_datasets():
    """
    Returns list of available demo datasets.
    """
    return {
        "success": True,
        "datasets": get_demo_datasets()
    }

@app.post("/api/load-demo")
def load_demo_dataset(demo_id: str = Body(..., embed=True)):
    """
    Loads a demo dataset and returns its profile (similar to upload).
    """
    try:
        # Get demo dataset path
        demo_path = get_demo_dataset_path(demo_id)
        
        if not os.path.exists(demo_path):
            raise HTTPException(status_code=404, detail="Demo dataset not found")
        
        # Generate unique file_id for this demo session
        file_id = f"{demo_id}_{uuid.uuid4().hex[:8]}"
        
        # Load and profile the demo data
        df = load_data(demo_path)
        profile = generate_profile(df)
        
        # Get demo metadata
        demo_info = next((d for d in get_demo_datasets() if d['id'] == demo_id), None)
        filename = demo_info['name'] if demo_info else demo_id
        
        # Generate visualization suggestions
        suggestions = generate_suggestions(profile)
        
        # Save to database (using demo path)
        save_file_metadata(file_id, filename, demo_path, profile)
        
        logger.info(f"Demo dataset loaded: {demo_id}")
        
        return {
            "file_id": file_id,
            "filename": filename,
            "profile": profile,
            "is_demo": True,
            "demo_info": demo_info,
            "suggestions": suggestions,
            "message": "Demo dataset loaded successfully."
        }
        
    except Exception as e:
        logger.error(f"Failed to load demo dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load demo: {str(e)}")

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """
    Uploads a CSV/Excel file, saves it, and returns a profile.
    """
    try:
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        file_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File saved to {save_path}. Loading data...")
        
        # Load and profile immediately to validate
        df = load_data(save_path)
        logger.info(f"Data loaded. Shape: {df.shape}. Generating profile...")
        
        profile = generate_profile(df)
        logger.info("Profile generated. Saving to DB...")
        
        # Save metadata to SQLite
        save_file_metadata(file_id, file.filename, save_path, profile)
        logger.info("Metadata saved to DB.")
        
        # Generate visualization suggestions
        suggestions = generate_suggestions(profile)
        logger.info(f"Generated {len(suggestions)} suggestions")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "profile": profile,
            "suggestions": suggestions,
            "message": "File uploaded and processed successfully."
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/generate")
def generate_chart(request: QueryRequest):
    """
    Generates a chart based on the user query and file ID.
    Now supports conversation memory.
    """
    # Validate session
    session = None
    if request.session_id:
        session = get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Retrieve from DB
    stored_data = get_file_metadata(request.file_id)
    
    if not stored_data:
        raise HTTPException(status_code=404, detail="File not found or session expired.")
        
    file_path = stored_data["path"]
    profile = stored_data["profile"]
    
    try:
        # Get conversation history if session exists
        conversation_history = []
        if request.session_id:
            conversation_history = get_conversation_history(request.session_id, request.file_id)
            logger.info(f"Using {len(conversation_history)} messages from history")
        
        # Load Data
        df = load_data(file_path)
        
        # 1. Brain: Generate Code with conversation context
        logger.info(f"Processing query using {request.provider}/{request.model}: {request.query}")
        brain_result = generate_visualization(
            profile, 
            request.query,
            conversation_history=conversation_history,
            provider=request.provider, 
            model=request.model
        )
        
        # Save user message to history
        if request.session_id:
            add_message(request.session_id, request.file_id, 'user', request.query)
        
        if brain_result["status"] != "success":
            # Save assistant response
            if request.session_id:
                add_message(request.session_id, request.file_id, 'assistant', brain_result["message"])
            
            return {
                "success": False,
                "message": brain_result["message"],
                "type": "text_response",
                "message_count": get_message_count(request.session_id, request.file_id) if request.session_id else 0
            }
        
        # Handle Text-Only Success (Q&A)
        if brain_result.get("type") == "text_response":
            # Save assistant response
            if request.session_id:
                add_message(request.session_id, request.file_id, 'assistant', brain_result["message"])
            
            return {
                "success": True,
                "message": brain_result["message"],
                "type": "text_response",
                "message_count": get_message_count(request.session_id, request.file_id) if request.session_id else 0
            }
            
        code = brain_result["code"]
        logger.info("Code generated successfully.")
        
        # 2. Executor: Run Code
        exec_result = execute_chart_code(code, df)
        
        if exec_result["success"]:
            # Save assistant response (chart description)
            if request.session_id:
                add_message(request.session_id, request.file_id, 'assistant', f"Generated chart for: {request.query}")
            
            return {
                "success": True,
                "image": exec_result["image"],
                "code": code,
                "message": "Chart generated.",
                "type": "image_response",
                "message_count": get_message_count(request.session_id, request.file_id) if request.session_id else 0
            }
        else:
            error_msg = f"Execution error: {exec_result['error']}"
            if request.session_id:
                add_message(request.session_id, request.file_id, 'assistant', error_msg)
            
            return {
                "success": False,
                "error": exec_result["error"],
                "code": code,
                "message": "Code generation produced an error during execution.",
                "type": "error_response",
                "message_count": get_message_count(request.session_id, request.file_id) if request.session_id else 0
            }
            
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
