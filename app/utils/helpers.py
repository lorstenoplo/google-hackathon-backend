import os
import shutil
from typing import List, Dict, Any

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary
    """
    os.makedirs(directory_path, exist_ok=True)

def cleanup_temp_files(file_paths: List[str]) -> None:
    """
    Clean up temporary files
    """
    for file_path in file_paths:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Error cleaning up {file_path}: {str(e)}")

def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """
    Format a standardized API response
    """
    return {
        "success": success,
        "message": message,
        "data": data
    }