import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging, log_requests
from src.models import ProcessConfig, ProcessingReport
from data_pipeline import create_cleaning_report, process_data, validate_dataframe

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
app.middleware("http")(log_requests)
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", 'version': '1.0.0'}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".csv":
        logger.warning(f"Rejected upload '{file.filename}': not a CSV file")
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as e:
        logger.warning(f"Could not parse '{file.filename}': {e}")
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}") from e
    


    dataset_id = storage.save_data(df, file.filename)
    logger.info(f"Saved dataset {dataset_id} from '{file.filename}' with {len(df)} rows")
    return storage.get_metadata(dataset_id)

@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get_data(dataset_id)
    if df is None:
        logger.warning(f"Dataset {dataset_id} not found")
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    records = json.loads(df.head(limit).to_json(orient="records"))
    logger.info(f"Retrieved {len(records)} row(s) from dataset {dataset_id}")
    return {
        "id": dataset_id,
        "data": records,
        "total_rows": len(df),
    }
    
@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""
    # TODO: retrieve, validate, process, report, update, and return.
    
    df = storage.get_data(dataset_id)
    if df is None:
        logger.warning(f"Dataset {dataset_id} not found")
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id}")
    try:
       validated = validate_dataframe( 
        df,
        required_columns=config.validation.required_columns,
        numeric_columns=config.validation.numeric_columns,
                                      )
       processed = process_data(validated, config.model_dump())
    except ValueError as e:
        logger.warning(f"Could not process dataset {dataset_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    validation_rows_removed = len(df) - len(validated)
    cleaning_report = create_cleaning_report(validated, processed)
    
    storage.update(dataset_id, processed)
    
    logger.info(f"Processed dataset {dataset_id}: {cleaning_report}")
    return{
        'id': dataset_id,
        'validation_rows_removed': validation_rows_removed,
        'cleaning_report': cleaning_report
    }