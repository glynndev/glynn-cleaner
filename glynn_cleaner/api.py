from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import io
import tempfile
import os

from glynn_cleaner import __version__
from glynn_cleaner.cleaner import clean_data
from glynn_cleaner.utils.logger import log_info, log_error


# ------------------------------------------------------------
# API KEY AUTHENTICATION
# ------------------------------------------------------------
API_KEY = "super-secret-key"  # Replace with environment variable later

def require_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ------------------------------------------------------------
# FASTAPI APP SETUP
# ------------------------------------------------------------
app = FastAPI(
    title="Glynn Cleaner API",
    description="API backend for the Glynn Cleaner CSV cleaning tool.",
    version=__version__,
)

# CORS (required for browser-based UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# ROOT ENDPOINT
# ------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Glynn Cleaner API is running",
        "version": __version__,
        "status": "ok"
    }


# ------------------------------------------------------------
# CLEAN ENDPOINT — RETURNS CLEANED CSV
# ------------------------------------------------------------
@app.post("/clean", dependencies=[Depends(require_api_key)])
async def clean_csv_api(
    file: UploadFile = File(...),
    mode: str = Form("simple"),
    strictness: str = Form("lenient"),
    summary_only: bool = Form(False),
    dry_run: bool = Form(False)
):
    """
    Upload a CSV file and return cleaned output as a downloadable CSV.
    """

    try:
        log_info("API request received — starting cleaning process")

        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            output_path = os.path.join(tmpdir, "output.csv")

            df.to_csv(input_path, index=False)

            clean_data(
                input_path=input_path,
                output_path=output_path,
                mode=mode,
                strictness=strictness,
                dry_run=dry_run,
                summary_only=summary_only
            )

            cleaned_bytes = open(output_path, "rb").read()

        return StreamingResponse(
            io.BytesIO(cleaned_bytes),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=cleaned_{file.filename}"
            }
        )

    except Exception as e:
        log_error(f"API error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ------------------------------------------------------------
# SUMMARY ENDPOINT — RETURNS SUMMARY JSON
# ------------------------------------------------------------
@app.post("/summary", dependencies=[Depends(require_api_key)])
async def clean_csv_summary_api(
    file: UploadFile = File(...),
    mode: str = Form("simple"),
    strictness: str = Form("lenient")
):
    """
    Upload a CSV and return ONLY the summary JSON.
    """

    try:
        log_info("API request received — summary mode")

        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            output_path = os.path.join(tmpdir, "output.csv")

            df.to_csv(input_path, index=False)

            clean_data(
                input_path=input_path,
                output_path=output_path,
                mode=mode,
                strictness=strictness,
                dry_run=False,
                summary_only=True
            )

            summary_path = output_path.replace(".csv", "_summary.csv")
            summary_df = pd.read_csv(summary_path)

        return summary_df.to_dict(orient="records")[0]

    except Exception as e:
        log_error(f"API summary error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# ------------------------------------------------------------
# REPORT ENDPOINT — RETURNS HUMAN-READABLE TEXT REPORT
# ------------------------------------------------------------
@app.post("/report", dependencies=[Depends(require_api_key)])
async def clean_csv_report_api(
    file: UploadFile = File(...),
    mode: str = Form("simple"),
    strictness: str = Form("lenient")
):
    """
    Upload a CSV and return the human-readable text report.
    """

    try:
        log_info("API request received — report mode")

        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            output_path = os.path.join(tmpdir, "output.csv")

            df.to_csv(input_path, index=False)

            clean_data(
                input_path=input_path,
                output_path=output_path,
                mode=mode,
                strictness=strictness,
                dry_run=False,
                summary_only=False
            )

            report_path = output_path.replace(".csv", "_report.txt")
            report_text = open(report_path, "r").read()

        return {"report": report_text}

    except Exception as e:
        log_error(f"API report error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

