#!/usr/bin/env python3
"""
api.py
======

FastAPI wrapper for the Pricing Point Entry document processing pipeline.

Serves the OpenAPI spec at /openapi.json and Swagger UI at /docs.

Usage:
    pip install fastapi uvicorn python-multipart
    python api.py

Then open http://localhost:8058/docs to upload a PDF + email and download JSON.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app import DocumentProcessingPipeline, PipelineConfig

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SCHEMA = PROJECT_ROOT / "prospect_schema.json"
OPENAPI_PATH = PROJECT_ROOT / "openapi.yaml"

app = FastAPI(
    title="Pricing Point Entry API",
    description="Upload PDF + email, download structured PricingPoint JSON.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _validate_upload(file: UploadFile, allowed_extensions: set[str], field_name: str) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail=f"{field_name} filename is missing")
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be one of: {', '.join(sorted(allowed_extensions))}",
        )


def _safe_filename(original: str, prefix: str) -> str:
    ext = Path(original).suffix.lower()
    return f"{prefix}_{uuid.uuid4().hex}{ext}"


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "schema": DEFAULT_SCHEMA.name,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post(
    "/api/v1/extract",
    tags=["Extraction"],
    summary="Extract PricingPoint prospect data",
    response_class=JSONResponse,
)
async def extract_prospect_data(
    pdf_file: UploadFile = File(..., description="GHQ or prospect PDF document"),
    email_file: UploadFile = File(..., description="Prospect email (.eml or .txt)"),
    no_rotation: bool = Form(False, description="Skip PDF rotation pre-processing"),
    extraction_method: str = Form(
        "auto",
        description="PDF extraction method: auto, pdfplumber, or schema_ocr",
    ),
):
    _validate_upload(pdf_file, {".pdf"}, "pdf_file")
    _validate_upload(email_file, {".eml", ".txt"}, "email_file")

    if extraction_method not in {"auto", "pdfplumber", "schema_ocr"}:
        raise HTTPException(
            status_code=400,
            detail="extraction_method must be one of: auto, pdfplumber, schema_ocr",
        )

    if not DEFAULT_SCHEMA.exists():
        raise HTTPException(status_code=500, detail=f"Schema not found: {DEFAULT_SCHEMA}")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured. Add it to your .env file.",
        )

    work_dir = Path(tempfile.mkdtemp(prefix="pricing_point_api_"))
    output_path = work_dir / "prospect_data.json"

    try:
        pdf_path = work_dir / _safe_filename(pdf_file.filename, "upload")
        email_path = work_dir / _safe_filename(email_file.filename, "upload")

        pdf_path.write_bytes(await pdf_file.read())
        email_path.write_bytes(await email_file.read())

        config = PipelineConfig()
        config.work_dir = str(work_dir / "pipeline_workspace")
        config.enable_rotation_fix = not no_rotation
        config.extraction_method = extraction_method
        config.keep_intermediate_files = True

        pipeline = DocumentProcessingPipeline(config)
        result = pipeline.run(
            pdf_path=str(pdf_path),
            email_path=str(email_path),
            schema_path=str(DEFAULT_SCHEMA),
            output_path=str(output_path),
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Pipeline failed"),
            )

        structured = result.get("outputs", {}).get("structured_data")
        if not structured and output_path.exists():
            structured = json.loads(output_path.read_text(encoding="utf-8"))

        if not structured:
            raise HTTPException(status_code=500, detail="Pipeline completed but produced no structured data")

        duration = result.get("duration_seconds", 0)
        account = structured.get("data", {}).get("location_name", "prospect")
        safe_account = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(account))
        filename = f"{safe_account or 'prospect'}_data.json"

        return JSONResponse(
            content=structured,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Processing-Duration-Seconds": str(duration),
            },
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    if OPENAPI_PATH.exists():
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(OPENAPI_PATH.read_text(encoding="utf-8"), media_type="text/yaml")
    raise HTTPException(status_code=404, detail="openapi.yaml not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8058, reload=True)
