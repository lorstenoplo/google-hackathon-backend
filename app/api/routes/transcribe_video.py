# app/routes/processing_routes.py
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
import os
import uuid
from typing import Optional, Dict, Any
from enum import Enum

from app.services.transcription_service import ProcessingService

class ProcessingType(str, Enum):
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    # Add more processing types as needed

router = APIRouter(prefix="/process", tags=["processing"])

# Define response models
class ProcessingResponse(BaseModel):
    task_id: str
    message: str
    file_path: str

class ProcessingResult(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory storage for task status (in production, use a database)
tasks: Dict[str, Dict[str, Any]] = {}

def get_processing_service():
    return ProcessingService()

@router.post("/{process_type}", response_model=ProcessingResponse)
async def process_file(
    process_type: ProcessingType,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_size: str = "base",
    options: Optional[Dict[str, Any]] = None,
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """
    Endpoint to upload a file and process it according to the specified process_type.
    
    Args:
        process_type: Type of processing to perform (transcription, translation, etc.)
        file: The file to process
        model_size: The size of the model to use
        options: Additional options for processing
    """
    if options is None:
        options = {}
    
    # Create unique task ID
    task_id = str(uuid.uuid4())
    
    # Create upload directory based on process type
    upload_dir = f"uploaded_{process_type.value}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Use task_id in filename to prevent collisions
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{task_id}{file_extension}"
    file_location = f"{upload_dir}/{safe_filename}"
    
    # Save uploaded file
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Create task record
    tasks[task_id] = {
        "status": "processing",
        "file_path": file_location,
        "process_type": process_type.value,
    }
    
    # Process the file in the background
    background_tasks.add_task(
        process_file_background,
        task_id=task_id,
        file_path=file_location,
        process_type=process_type.value,
        model_size=model_size,
        options=options,
        processing_service=processing_service
    )
    
    return ProcessingResponse(
        task_id=task_id,
        message=f"File uploaded and {process_type.value} task started",
        file_path=file_location
    )

async def process_file_background(
    task_id: str,
    file_path: str,
    process_type: str,
    model_size: str,
    options: Dict[str, Any],
    processing_service: ProcessingService
):
    """Background task to process the file."""
    try:
        # Process based on type
        if process_type == ProcessingType.TRANSCRIPTION.value:
            result = processing_service.transcribe(file_path, model_size, **options)
        elif process_type == ProcessingType.TRANSLATION.value:
            result = processing_service.translate(file_path, model_size, **options)
        elif process_type == ProcessingType.SUMMARIZATION.value:
            result = processing_service.summarize(file_path, model_size, **options)
        else:
            raise ValueError(f"Unsupported process type: {process_type}")
        
        # Update task status
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = result
    
    except Exception as e:
        # Handle errors
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@router.get("/{task_id}", response_model=ProcessingResult)
async def get_processing_result(task_id: str):
    """Get the result of a processing task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]

    print(f"Task ID: {task_id}, Status: {task['status']}, Result: {task.get('result')}, Error: {task.get('error')}")
    
    return ProcessingResult(
        task_id=task_id,
        status=task["status"],
        result=task.get("result"),
        error=task.get("error")
    )

# Convenience endpoint for transcription (maintains backward compatibility)
@router.post("/transcribe", response_model=ProcessingResponse)
async def transcribe_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_size: str = "base",
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """Shortcut endpoint for transcription."""
    return await process_file(
        ProcessingType.TRANSCRIPTION,
        background_tasks,
        file=file,
        model_size=model_size,
        processing_service=processing_service
    )