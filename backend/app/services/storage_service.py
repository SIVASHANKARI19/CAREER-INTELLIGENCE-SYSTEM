import os
import uuid
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def save_uploaded_pdf(file: UploadFile, student_id: int, file_prefix: str) -> str:
    filename = file.filename or "uploaded.pdf"
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension {ext}. Only PDF files are allowed."
        )

    # Read content to verify size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10MB."
        )
    
    unique_filename = f"{file_prefix}_student_{student_id}_{uuid.uuid4().hex[:8]}.pdf"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path
