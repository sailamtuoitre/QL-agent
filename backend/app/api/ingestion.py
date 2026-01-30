from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.config import settings
import os
import uuid
from datetime import datetime
import pandas as pd
from io import BytesIO
from pydantic import ValidationError
from app.schemas.sales import SalesBatch

router = APIRouter()

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

def validate_file_extension(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        )
    return ext

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a raw sales data file (Excel or CSV).
    The file will be saved to the 'raw' data directory and queued for processing.
    """
    # 1. Validate extension
    ext = validate_file_extension(file.filename)
    
    # 2. Read content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {str(e)}")

    # 3. Parse with Pandas
    try:
        if ext == '.csv':
            df = pd.read_csv(BytesIO(content))
        else:
            df = pd.read_excel(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {str(e)}")

    # 4. Validate with Pydantic
    try:
        # Data cleaning: normalize columns and handle NaNs
        df.columns = df.columns.str.lower().str.strip()
        df = df.replace({float('nan'): None})
        records = df.to_dict(orient='records')
        
        # Validation
        validated_batch = SalesBatch(root=records)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"Data validation error: {str(e)}")

    # 5. Generate unique filename (uuid + timestamp) to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_id = str(uuid.uuid4())
    safe_filename = f"{timestamp}_{file_id}{ext}"
    file_path = os.path.join(settings.RAW_DATA_DIR, safe_filename)
    
    # 6. Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
        
    # TODO: Trigger Celery Task here (Next Step)
    
    return {
        "file_id": file_id,
        "filename": safe_filename,
        "original_filename": file.filename,
        "status": "uploaded",
        "message": "File uploaded successfully. Processing queued.",
        "record_count": len(validated_batch.root)
    }
