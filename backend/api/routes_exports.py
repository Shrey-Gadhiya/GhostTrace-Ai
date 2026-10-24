from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any
from pathlib import Path
import zipfile
import csv
import json
from backend.config import settings
from backend.engine.loader import DatasetLoader
from backend.engine.audit_runner import AuditRunner
from backend.engine.csv_writer import OutputCSVWriter
from backend.ai.cost_tracker import tracker

router = APIRouter()
loader = DatasetLoader()
loader.load_all()

@router.get("/submission/status")
def get_submission_status():
    output_exists = settings.OUTPUT_FILE.exists()
    output_rows = 0
    if output_exists:
        try:
            with open(settings.OUTPUT_FILE, "r", encoding="utf-8") as f:
                output_rows = sum(1 for _ in csv.DictReader(f))
        except Exception:
            output_rows = 0

    zip_file = settings.BASE_DIR / "code.zip"
    eval_rep = settings.BASE_DIR / "evaluation" / "evaluation_report.md"
    usage_rep = settings.BASE_DIR / "evaluation" / "usage_report.md"

    return {
        "artifacts": {
            "output_csv": {
                "file_path": "output.csv",
                "exists": output_exists,
                "row_count": output_rows,
                "expected_rows": len(loader.requests),
                "is_ready": (output_exists and output_rows == len(loader.requests))
            },
            "code_zip": {
                "file_path": "code.zip",
                "exists": zip_file.exists(),
                "size_bytes": zip_file.stat().st_size if zip_file.exists() else 0,
                "is_ready": zip_file.exists()
            },
            "evaluation_report": {
                "file_path": "evaluation/evaluation_report.md",
                "exists": eval_rep.exists(),
                "size_bytes": eval_rep.stat().st_size if eval_rep.exists() else 0,
                "is_ready": eval_rep.exists()
            },
            "usage_report": {
                "file_path": "evaluation/usage_report.md",
                "exists": usage_rep.exists(),
                "size_bytes": usage_rep.stat().st_size if usage_rep.exists() else 0,
                "is_ready": usage_rep.exists()
            }
        },
        "all_ready": (output_exists and output_rows == len(loader.requests) and zip_file.exists() and eval_rep.exists() and usage_rep.exists())
    }

@router.post("/exports/output-csv")
def export_output_csv():
    runner = AuditRunner(loader)
    results = runner.audit_all()
    target_path = OutputCSVWriter.write_output_csv(results, settings.OUTPUT_FILE)
    return {
        "status": "success",
        "output_path": str(target_path),
        "total_cases": len(results)
    }

@router.post("/exports/submission-zip")
def create_submission_zip():
    base_dir = settings.BASE_DIR
    zip_path = base_dir / "code.zip"

    # Exclude patterns
    excluded_dirs = {".git", ".gemini", "node_modules", ".venv", "__pycache__", ".pytest_cache", "dist", "build"}
    excluded_exts = {".pyc", ".pyo", ".env"}

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in base_dir.rglob("*"):
            # Check exclusions
            if any(part in excluded_dirs for part in file.parts):
                continue
            if file.suffix in excluded_exts or file.name in [".env", "code.zip"]:
                continue
            if file.is_file():
                rel_path = file.relative_to(base_dir)
                zipf.write(file, arcname=str(rel_path))

    return {
        "status": "success",
        "zip_path": str(zip_path),
        "size_bytes": zip_path.stat().st_size
    }

@router.get("/downloads/{artifact_id}")
def download_artifact(artifact_id: str):
    file_map = {
        "output-csv": settings.OUTPUT_FILE,
        "code-zip": settings.BASE_DIR / "code.zip",
        "evaluation-report": settings.BASE_DIR / "evaluation" / "evaluation_report.md",
        "usage-report": settings.BASE_DIR / "evaluation" / "usage_report.md"
    }

    target = file_map.get(artifact_id)
    if not target or not target.exists():
        raise HTTPException(status_code=404, detail=f"Artifact '{artifact_id}' not found")

    return FileResponse(
        path=str(target),
        filename=target.name,
        media_type="application/octet-stream"
    )
