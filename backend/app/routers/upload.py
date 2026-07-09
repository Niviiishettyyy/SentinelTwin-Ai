import csv
import io
from fastapi import APIRouter, UploadFile, File, Depends
from app.graph.twin import twin
from app import auth

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("")
async def upload_flows(file: UploadFile = File(...), current_user=Depends(auth.get_current_user)):
    """
    Admin-only utility (Section 7.8 / 12): seed/backfill the twin from an
    offline CSV of flow records when live telemetry isn't available.
    """
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    count = 0
    for row in reader:
        twin._ingest_flow(row)
        count += 1
    return {"ingested_rows": count}
