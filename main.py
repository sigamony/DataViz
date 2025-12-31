from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
import logging

# Import our modules
from src.dataloader import load_data, generate_profile
from src.brain import generate_visualization
from src.executor import execute_chart_code
from src.database import init_db, save_file_metadata, get_file_metadata

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Chart Visualizer API")

# Initialize Database on startup
init_db()

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
    provider: str = "gemini"
    model: str = "gemini-2.5-flash-lite"

from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse('index.html')

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a CSV/Excel file, saves it, and returns a profile.
    """
    try:
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
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
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "profile": profile,
            "message": "File uploaded and processed successfully."
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/generate")
async def generate_chart(request: QueryRequest):
    """
    Generates a chart based on the user query and file ID.
    """
    # Retrieve from DB
    stored_data = get_file_metadata(request.file_id)
    
    if not stored_data:
        raise HTTPException(status_code=404, detail="File not found or session expired.")
        
    file_path = stored_data["path"]
    profile = stored_data["profile"]
    
    try:
        # Load Data (we could cache df in memory but for safety/memory we reload)
        df = load_data(file_path)
        
        # 1. Brain: Generate Code
        # We pass the profile and query to the LLM
        logger.info(f"Processing query using {request.provider}/{request.model}: {request.query}")
        brain_result = generate_visualization(
            profile, 
            request.query, 
            provider=request.provider, 
            model=request.model
        )
        
        if brain_result["status"] != "success":
            return {
                "success": False,
                "message": brain_result["message"],
                "type": "text_response" 
            }
        
        # New: Handle Text-Only Success (Q&A)
        if brain_result.get("type") == "text_response":
             return {
                "success": True,
                "message": brain_result["message"],
                "type": "text_response"
            }
            
        code = brain_result["code"]
        logger.info("Code generated successfully.")
        
        # 2. Executor: Run Code
        exec_result = execute_chart_code(code, df)
        
        if exec_result["success"]:
            return {
                "success": True,
                "image": exec_result["image"], # Base64 string
                "code": code,
                "message": "Chart generated.",
                "type": "image_response"
            }
        else:
            return {
                "success": False,
                "error": exec_result["error"],
                "code": code,
                "message": "Code generation produced an error during execution.",
                "type": "error_response"
            }
            
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
