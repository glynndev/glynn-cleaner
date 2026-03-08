from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import tempfile
import os
import subprocess

app = FastAPI()


@app.post("/clean")
async def clean_file(
    file: UploadFile = File(...),
    mode: str = Form("simple"),
    strictness: str = Form("lenient"),
):
    # 1. Save uploaded file to a temporary CSV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_in:
        tmp_in.write(await file.read())
        input_path = tmp_in.name

    # 2. Define output path
    output_path = input_path.replace(".csv", "_cleaned.csv")

    # 3. Call your existing CLI tool
    #    glynn-cleaner --input <in> --output <out> --mode <mode> --strictness <strictness>
    subprocess.run(
        [
            "glynn-cleaner",
            "--input",
            input_path,
            "--output",
            output_path,
            "--mode",
            mode,
            "--strictness",
            strictness,
        ],
        check=True,
    )

    # 4. Return the cleaned file
    return FileResponse(
        output_path,
        filename="cleaned.csv",
        media_type="text/csv",
    )
