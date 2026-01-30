import os
import pandas as pd
from loguru import logger
from app.workers.celery_app import celery_app
from app.core.config import settings

@celery_app.task(name="app.workers.tasks.process_sales_file")
def process_sales_file(file_path: str):
    """
    Task to convert a raw sales file (CSV/Excel) to Parquet.
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"status": "error", "message": "File not found"}

        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1].lower()

        logger.info(f"Processing file: {filename}")

        # 1. Read the file
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path)
        else:
            logger.error(f"Unsupported extension: {ext}")
            return {"status": "error", "message": f"Unsupported extension: {ext}"}

        # 2. Basic cleaning (normalize columns)
        df.columns = df.columns.str.lower().str.strip()
        
        # 3. Save as Parquet
        processed_filename = f"{name_without_ext}.parquet"
        processed_path = os.path.join(settings.PROCESSED_DATA_DIR, processed_filename)
        
        # Ensure processed directory exists (just in case)
        os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
        
        df.to_parquet(processed_path, index=False, engine="pyarrow")
        
        logger.info(f"Successfully converted {filename} to {processed_filename}")
        
        return {
            "status": "success",
            "original_file": filename,
            "processed_file": processed_filename,
            "rows": len(df)
        }

    except Exception as e:
        logger.exception(f"Error processing file {file_path}: {str(e)}")
        return {"status": "error", "message": str(e)}
