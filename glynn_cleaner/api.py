from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import tempfile
import os
import json
import uuid
import logging
import time
import sqlite3
import stripe
from collections import defaultdict

from glynn_cleaner import __version__
from glynn_cleaner.cleaner import clean_data
from glynn_cleaner.utils.logger import log_info, log_error
from pydantic import BaseModel, RootModel

# ------------------------------------------------------------
# UTILITY: Save uploaded file to disk
# ------------------------------------------------------------
async def save_upload_to_disk(upload_file: UploadFile, destination_path: str):
    with open(destination_path, "wb") as buffer:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            buffer.write(chunk)

# ------------------------------------------------------------
# JSON LOGGING SETUP
# ------------------------------------------------------------
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        })

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

# ------------------------------------------------------------
# RESPONSE MODELS
# ------------------------------------------------------------
class StatusResponse(BaseModel):
    status: str
    version: str | None = None
    message: str | None = None

class ErrorResponse(BaseModel):
    error: str

class ReportResponse(BaseModel):
    report: str

class SummaryResponse(RootModel[dict]):
    pass

class SchemaResponse(BaseModel):
    schema: dict

class PreviewResponse(BaseModel):
    preview: list

class ColumnsResponse(BaseModel):
    columns: list[str]

class ProfileResponse(BaseModel):
    profile: dict

class DelimiterResponse(BaseModel):
    delimiter: str

class InferredTypesResponse(BaseModel):
    types: dict

# ------------------------------------------------------------
# GLOBAL LIMITS & METRICS
# ------------------------------------------------------------
RATE_LIMIT = 60
RATE_WINDOW = 60
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

START_TIME = time.time()
TOTAL_REQUESTS = 0
RATE_LIMIT_HITS = 0
request_log = defaultdict(list)


# ------------------------------------------------------------
# SQLITE DATABASE
# ------------------------------------------------------------
DB_PATH = "glynn_cleaner.db"

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    rows INTEGER,
    billable_units INTEGER,
    estimated_cost REAL,
    status TEXT,
    created_at TEXT
)
""")

conn.commit()

try:
    cursor.execute("""
    ALTER TABLE jobs
    ADD COLUMN output_file TEXT
    """)
    conn.commit()
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("""
    ALTER TABLE jobs
    ADD COLUMN input_file TEXT
    """)
    conn.commit()
except sqlite3.OperationalError:
    pass


# ------------------------------------------------------------
# API KEY AUTH
# ------------------------------------------------------------
raw_keys = os.getenv("API_KEYS", "").split(",")
API_KEYS = {}

for entry in raw_keys:
    if ":" in entry:
        name, key = entry.split(":", 1)
        API_KEYS[key.strip()] = name.strip()
    else:
        API_KEYS[entry.strip()] = "unnamed"

if not API_KEYS:
    raise RuntimeError("API_KEYS environment variable is not set")

def require_api_key(x_api_key: str = Header(None)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    log_info(f"API key used: {API_KEYS.get(x_api_key)}")

print("Loaded API keys:", API_KEYS)

# ------------------------------------------------------------
# FASTAPI SETUP (CLEAN + CORRECT)
# ------------------------------------------------------------
app = FastAPI(
    title="Glynn Cleaner API",
    description="API backend for the Glynn Cleaner CSV cleaning tool.",
    version=__version__,
    openapi_tags=[
        {"name": "System", "description": "Health checks and service metadata."},
        {"name": "Cleaning", "description": "CSV cleaning and summaries."},
        {"name": "Reporting", "description": "Human-readable reports."}
    ]
)

# ------------------------------------------------------------
# CUSTOM OPENAPI (FIXED + CLEAN)
# ------------------------------------------------------------
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    print("CUSTOM OPENAPI EXECUTED")
    app.openapi_schema = None

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # ------------------------------------------------------------
    # SECURITY SCHEME
    # ------------------------------------------------------------
    schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    for path in schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"APIKeyHeader": []}])

    # ------------------------------------------------------------
    # FORCE /clean TO BE A FILE DOWNLOAD
    # ------------------------------------------------------------
    if "/clean" in schema["paths"]:
        post_op = schema["paths"]["/clean"]["post"]

    # Ensure the 200 response exists
    if "200" not in post_op["responses"]:
        post_op["responses"]["200"] = {}

    # Ensure the content block exists
    if "content" not in post_op["responses"]["200"]:
        post_op["responses"]["200"]["content"] = {}

    # Remove JSON fallback if present
    if "application/json" in post_op["responses"]["200"]["content"]:
        del post_op["responses"]["200"]["content"]["application/json"]

    # Replace entire content block with ONLY binary types
    post_op["responses"]["200"]["content"] = {
        "text/csv": {
            "schema": {
                "type": "string",
                "format": "binary"
            }
        },
        "application/octet-stream": {
            "schema": {
                "type": "string",
                "format": "binary"
            }
        }
    }


    app.openapi_schema = schema
    return schema

# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://app.glynncleaner.com"
    ],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# MIDDLEWARE: File size limit
# ------------------------------------------------------------
@app.middleware("http")
async def enforce_file_size_limit(request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_UPLOAD_SIZE:
        return JSONResponse(
            status_code=413,
            content={
                "error": "File too large.",
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        )
    return await call_next(request)

# ------------------------------------------------------------
# MIDDLEWARE: Rate limiting
# ------------------------------------------------------------
@app.middleware("http")
async def rate_limit(request, call_next):
    global RATE_LIMIT_HITS

    ip = request.client.host
    now = time.time()

    request_log[ip] = [ts for ts in request_log[ip] if now - ts < RATE_WINDOW]

    if len(request_log[ip]) >= RATE_LIMIT:
        RATE_LIMIT_HITS += 1
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})

    request_log[ip].append(now)
    return await call_next(request)

# ------------------------------------------------------------
# MIDDLEWARE: Logging
# ------------------------------------------------------------
@app.middleware("http")
async def log_requests(request, call_next):
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1

    start = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start).total_seconds()

    logging.info(json.dumps({
        "request_id": getattr(request.state, "request_id", "unknown"),
        "client_ip": request.client.host,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration": duration
    }))

    return response

# ------------------------------------------------------------
# MIDDLEWARE: Request ID
# ------------------------------------------------------------
@app.middleware("http")
async def attach_request_id(request, call_next):
    if not hasattr(request.state, "request_id"):
        request.state.request_id = str(uuid.uuid4())

    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

# ------------------------------------------------------------
# SYSTEM ENDPOINTS
# ------------------------------------------------------------
@app.get("/health", response_model=StatusResponse, tags=["System"])
def health():
    return StatusResponse(status="ok")

@app.get("/", response_model=StatusResponse, tags=["System"])
def root():
    return StatusResponse(status="ok", version=__version__, message="Glynn Cleaner API is running")

@app.get("/metrics", tags=["System"])
def metrics():
    return {
        "status": "ok",
        "version": __version__,
        "uptime_seconds": time.time() - START_TIME,
        "total_requests": TOTAL_REQUESTS,
        "rate_limit_hits": RATE_LIMIT_HITS,
        "active_api_keys": len(API_KEYS)
    }

# ------------------------------------------------------------
# CLEAN ENDPOINT (CSV DOWNLOAD WORKING)
# ------------------------------------------------------------
@app.post(
    "/clean",
    dependencies=[Depends(require_api_key)],
    tags=["Cleaning"],
    response_class=StreamingResponse
)
async def clean_csv_api(
    file: UploadFile = File(...),
    mode: str = Form("simple"),
    strictness: str = Form("lenient"),
    summary_only: bool = Form(False),
    dry_run: bool = Form(False)
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            output_path = os.path.join(tmpdir, "output.csv")

            await save_upload_to_disk(file, input_path)

            df = pd.read_csv(input_path)

            # --- PRICING / PAYWALL LOGIC ---
            rows = len(df)

            FREE_LIMIT = 5000
            billable_units = (rows + 999) // 1000
            unit_price = 0.25
            cost = billable_units * unit_price

            if rows > FREE_LIMIT:
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "payment_required",
                        "rows": rows,
                        "billable_units": billable_units,
                        "estimated_cost": cost,
                        "free_limit": FREE_LIMIT
                    }
                )
            # --- END PAYWALL ---

            df.to_csv(input_path, index=False)

            clean_data(
                input_path=input_path,
                output_path=output_path,
                mode=mode,
                strictness=strictness,
                dry_run=dry_run,
                summary_only=summary_only
            )

            def iter_file(path):
                with open(path, "rb") as f:
                    while chunk := f.read(1024 * 1024):
                        yield chunk

            return StreamingResponse(
                iter_file(output_path),
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename=cleaned_{file.filename}"
                }
            )

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------------------------------------------------
# SCHEMA ENDPOINT
# ------------------------------------------------------------
@app.post(
    "/schema",
    dependencies=[Depends(require_api_key)],
    tags=["Cleaning"],
    response_model=SchemaResponse
)
async def schema_csv_api(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            await save_upload_to_disk(file, input_path)
            df = pd.read_csv(input_path)

        schema = {
            "columns": {},
            "row_count": len(df)
        }

        for col in df.columns:
            col_data = df[col]
            schema["columns"][col] = {
                "dtype": str(col_data.dtype),
                "missing": int(col_data.isna().sum()),
                "sample_values": col_data.dropna().head(5).tolist()
            }

        return SchemaResponse(schema=schema)

    except Exception as e:
        log_error(str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ------------------------------------------------------------
# PREVIEW ENDPOINT
# ------------------------------------------------------------
@app.post("/preview", dependencies=[Depends(require_api_key)], tags=["Cleaning"], response_model=PreviewResponse)
async def preview_csv_api(file: UploadFile = File(...), rows: int = Form(5)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            await save_upload_to_disk(file, input_path)
            df = pd.read_csv(input_path)

        rows = max(1, min(rows, 50))
        preview_data = df.head(rows).to_dict(orient="records")

        return PreviewResponse(preview=preview_data)

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------------------------------------------------
# COLUMNS ENDPOINT
# ------------------------------------------------------------
@app.post("/columns", dependencies=[Depends(require_api_key)], tags=["Cleaning"], response_model=ColumnsResponse)
async def columns_csv_api(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            await save_upload_to_disk(file, input_path)
            df = pd.read_csv(input_path)

        return ColumnsResponse(columns=list(df.columns))

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------------------------------------------------
# PROFILE ENDPOINT
# ------------------------------------------------------------
@app.post("/profile", dependencies=[Depends(require_api_key)], tags=["Cleaning"], response_model=ProfileResponse)
async def profile_csv_api(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            await save_upload_to_disk(file, input_path)
            df = pd.read_csv(input_path)

        profile = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": {}
        }

        for col in df.columns:
            col_data = df[col]
            col_profile = {
                "dtype": str(col_data.dtype),
                "missing": int(col_data.isna().sum()),
                "unique": int(col_data.nunique(dropna=True)),
                "sample_values": col_data.dropna().head(5).tolist()
            }

            if pd.api.types.is_numeric_dtype(col_data):
                col_profile["min"] = float(col_data.min(skipna=True))
                col_profile["max"] = float(col_data.max(skipna=True))
                col_profile["mean"] = float(col_data.mean(skipna=True))
                col_profile["std"] = float(col_data.std(skipna=True))

            if pd.api.types.is_string_dtype(col_data):
                lengths = col_data.dropna().astype(str).str.len()
                if not lengths.empty:
                    col_profile["text_length_min"] = int(lengths.min())
                    col_profile["text_length_max"] = int(lengths.max())
                    col_profile["text_length_mean"] = float(lengths.mean())

            profile["columns"][col] = col_profile

        return ProfileResponse(profile=profile)

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------------------------------------------------
# DETECT DELIMITER ENDPOINT
# ------------------------------------------------------------
@app.post("/detect-delimiter", dependencies=[Depends(require_api_key)], tags=["Cleaning"], response_model=DelimiterResponse)
async def detect_delimiter_api(file: UploadFile = File(...)):
    try:
        sample = (await file.read(4096)).decode("utf-8", errors="ignore")
        await file.seek(0)

        import csv
        sniffer = csv.Sniffer()

        try:
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ","

        return DelimiterResponse(delimiter=delimiter)

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------------------------------------------------
# INFER TYPES ENDPOINT
# ------------------------------------------------------------
@app.post("/infer-types", dependencies=[Depends(require_api_key)], tags=["Cleaning"], response_model=InferredTypesResponse)
async def infer_types_api(file: UploadFile = File(...)):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            await save_upload_to_disk(file, input_path)
            df = pd.read_csv(input_path)

        inferred = {}

        import re
        email_re = re.compile(r"[^@]+@[^@]+\.[^@]+")
        phone_re = re.compile(r"^\+?\d[\d\s\-()]{6,}$")
        url_re = re.compile(r"^https?://")
        currency_re = re.compile(r"^[£$€]\s?\d")
        postcode_re = re.compile(r"^[A-Za-z]{1,2}\d[A-Za-z\d]?\s*\d[A-Za-z]{2}$")

        for col in df.columns:
            col_data = df[col].dropna().astype(str)

            if col_data.empty:
                inferred[col] = "unknown"
                continue

            sample = col_data.head(20)

            if sample.apply(lambda x: bool(email_re.match(x))).mean() > 0.6:
                inferred[col] = "email"
                continue

            if sample.apply(lambda x: bool(phone_re.match(x))).mean() > 0.6:
                inferred[col] = "phone"
                continue

            if sample.apply(lambda x: bool(url_re.match(x))).mean() > 0.6:
                inferred[col] = "url"
                continue

            if sample.apply(lambda x: bool(currency_re.match(x))).mean() > 0.6:
                inferred[col] = "currency"
                continue

            if sample.apply(lambda x: bool(postcode_re.match(x))).mean() > 0.6:
                inferred[col] = "postcode"
                continue

            if sample.str.lower().isin(["true", "false", "yes", "no", "0", "1"]).mean() > 0.8:
                inferred[col] = "boolean"
                continue

            try:
                pd.to_datetime(sample, errors="raise")
                inferred[col] = "datetime"
                continue
            except Exception:
                pass

            if pd.api.types.is_numeric_dtype(df[col]):
                inferred[col] = "numeric"
                continue

            if df[col].nunique() / max(len(df), 1) < 0.05:
                inferred[col] = "categorical"
                continue

            inferred[col] = "text"

        return InferredTypesResponse(types=inferred)

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

# ------------------------------------------------------------
# REPORT ENDPOINT
# ------------------------------------------------------------
@app.post("/report", dependencies=[Depends(require_api_key)], tags=["Reporting"], response_model=ReportResponse)
async def clean_csv_report_api(
    file: UploadFile = File(...),
    mode: str = Form("simple"),
    strictness: str = Form("lenient")
):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            await save_upload_to_disk(file, input_path)
            df = pd.read_csv(input_path)

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

        return ReportResponse(report=report_text)

    except Exception as e:
            log_error(str(e))
            return JSONResponse(status_code=500, content={"error": str(e)})

print("API FILE LOADED")
app.openapi = custom_openapi
print("OPENAPI OVERRIDE ATTACHED")

from io import StringIO
import csv

@app.post("/quote", tags=["Cleaning"])
async def quote_csv_api(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = contents.decode("utf-8", errors="ignore")

        reader = csv.reader(StringIO(text))
        rows = max(0, sum(1 for _ in reader) - 1)

        billable_units = (rows + 999) // 1000
        unit_price = 0.25
        cost = billable_units * unit_price

        job_id = str(uuid.uuid4())

        input_file = f"input/{job_id}.csv"

        with open(input_file, "wb") as f:
            f.write(contents)

        cursor.execute("""
        INSERT INTO jobs (
            job_id,
            rows,
            billable_units,
            estimated_cost,
            status,
            created_at,
            input_file
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            rows,
            billable_units,
            cost,
            "awaiting_payment",
            datetime.utcnow().isoformat(),
            input_file
        ))

        conn.commit()

        return {
            "job_id": job_id,
            "rows": rows,
            "billable_units": billable_units,
            "estimated_cost": cost,
            "tier": "free" if rows <= 5000 else "payg",
            "status": "free" if rows <= 5000 else "awaiting_payment"
        }

    except Exception as e:
        log_error(str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/job/{job_id}", tags=["Cleaning"])
async def get_job(job_id: str):
    cursor.execute("""
    SELECT rows,
           billable_units,
           estimated_cost,
           status
    FROM jobs
    WHERE job_id = ?
    """, (job_id,))

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "job_not_found"}
        )

    return {
        "rows": row[0],
        "billable_units": row[1],
        "estimated_cost": row[2],
        "status": row[3]
    }  


@app.post("/job/{job_id}/pay", tags=["Cleaning"])
async def pay_for_job(job_id: str):
    cursor.execute("""
    UPDATE jobs
    SET status = ?
    WHERE job_id = ?
    """, ("paid", job_id))

    conn.commit()

    if cursor.rowcount == 0:
        return JSONResponse(
            status_code=404,
            content={"error": "job_not_found"}
        )

    return {
        "job_id": job_id,
        "status": "paid"
    }  

@app.post("/job/{job_id}/checkout", tags=["Payments"])
async def create_checkout_session(job_id: str):

    cursor.execute("""
    SELECT estimated_cost, status
    FROM jobs
    WHERE job_id = ?
    """, (job_id,))

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "job_not_found"}
        )

    amount = row[0]
    status = row[1]

    if status != "awaiting_payment":
        return JSONResponse(
            status_code=400,
            content={"error": "job_not_awaiting_payment"}
        )

    session = stripe.checkout.Session.create(
        mode="payment",

        metadata={
            "job_id": job_id
        },

        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"CSV Cleaning Job {job_id}"
                    },
                    "unit_amount": int(amount * 100)
                },
                "quantity": 1
            }
        ],
        success_url="http://127.0.0.1:8000/docs",
        cancel_url="http://127.0.0.1:8000/docs"
    )

    return {
        "checkout_url": session.url
    }

@app.post("/stripe/webhook", tags=["Payments"])
async def stripe_webhook(request: Request):

    payload = await request.json()

    event = stripe.Event.construct_from(
        payload,
        stripe.api_key
    )

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        job_id = session["metadata"]["job_id"]

        cursor.execute("""
        UPDATE jobs
        SET status = ?
        WHERE job_id = ?
        """, ("paid", job_id))

        conn.commit()

        print(f"Payment confirmed for job {job_id}")

    return {"received": True}


@app.post("/job/{job_id}/process", tags=["Cleaning"])
async def process_job(job_id: str):
    cursor.execute("""
    SELECT status, input_file
    FROM jobs
    WHERE job_id = ?
    """, (job_id,))

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "job_not_found"}
        )

    if row[0] != "paid":
        return JSONResponse(
            status_code=400,
            content={"error": "job_not_paid"}
        )

    input_file = row[1]

    output_file = f"output/{job_id}.csv"

    clean_data(
        input_path=input_file,
        output_path=output_file,
        mode="simple",
        strictness="lenient"
    )

    cursor.execute("""
    UPDATE jobs
    SET status = ?,
        output_file = ?
    WHERE job_id = ?
    """, (
        "completed",
        output_file,
        job_id
    ))

    conn.commit()

    return {
        "job_id": job_id,
        "status": "completed"
    }

@app.get("/job/{job_id}/download", tags=["Cleaning"])
async def download_job(job_id: str):

    cursor.execute("""
    SELECT output_file
    FROM jobs
    WHERE job_id = ?
    """, (job_id,))

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "job_not_found"}
        )

    output_file = row[0]

    if not output_file:
        return JSONResponse(
            status_code=400,
            content={"error": "job_not_processed"}
        )

    if not os.path.exists(output_file):
        return JSONResponse(
            status_code=404,
            content={"error": "output_file_missing"}
        )

    return FileResponse(
        output_file,
        filename=os.path.basename(output_file),
        media_type="text/csv"
    )
