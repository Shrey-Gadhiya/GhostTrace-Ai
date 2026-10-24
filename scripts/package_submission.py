#!/usr/bin/env python3
"""
GhostTrace AI — Submission Packaging Script
Packages clean runnable codebase into code.zip excluding node_modules, .venv, caches, and secrets.
Validates all challenge deliverables before finalizing.
"""

import sys
import os
import zipfile
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def validate_deliverables():
    print("=" * 70)
    print("  Validating Challenge Deliverables Prior to Packaging")
    print("=" * 70)

    # 1. Check output.csv
    out_file = BASE_DIR / "output.csv"
    if not out_file.exists():
        raise FileNotFoundError("Missing output.csv! Please run scripts/run_audit.py first.")

    with open(out_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["case_id", "deletion_status", "steps_json"]:
            raise ValueError(f"Invalid columns in output.csv: {reader.fieldnames}")
        row_count = sum(1 for _ in reader)

    if row_count != 518:
        raise ValueError(f"output.csv must have exactly 518 rows, found {row_count}")
    print(f"  [OK] output.csv verified: 518 rows, strict 3-column schema.")

    # 2. Check evaluation reports
    eval_rep = BASE_DIR / "evaluation" / "evaluation_report.md"
    if not eval_rep.exists():
        raise FileNotFoundError("Missing evaluation/evaluation_report.md! Run scripts/evaluate.py first.")
    print(f"  [OK] evaluation/evaluation_report.md verified ({eval_rep.stat().st_size} bytes).")

    usage_rep = BASE_DIR / "evaluation" / "usage_report.md"
    if not usage_rep.exists():
        raise FileNotFoundError("Missing evaluation/usage_report.md! Run scripts/evaluate.py first.")
    print(f"  [OK] evaluation/usage_report.md verified ({usage_rep.stat().st_size} bytes).")

    # 3. Check README.md
    readme = BASE_DIR / "README.md"
    if not readme.exists():
        print("  [WARN] README.md pending.")
    else:
        print(f"  [OK] README.md verified ({readme.stat().st_size} bytes).")

def create_zip():
    zip_path = BASE_DIR / "code.zip"
    print(f"\nBuilding submission bundle: {zip_path}")

    excluded_dirs = {
        ".git", ".gemini", "node_modules", ".venv", "venv",
        "__pycache__", ".pytest_cache", ".system_generated",
        "dist", "build", ".idea", ".vscode"
    }
    excluded_exts = {".pyc", ".pyo", ".pyd"}
    excluded_files = {".env", "code.zip"}

    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in BASE_DIR.rglob("*"):
            if not file.is_file():
                continue
            
            # Check exclusions
            parts = file.relative_to(BASE_DIR).parts
            if any(p in excluded_dirs for p in parts):
                continue
            if file.suffix in excluded_exts or file.name in excluded_files:
                continue

            rel_path = file.relative_to(BASE_DIR)
            zipf.write(file, arcname=str(rel_path))
            file_count += 1
            total_bytes += file.stat().st_size

    zip_size = zip_path.stat().st_size
    print(f"  [SUCCESS] Packaged {file_count} files ({total_bytes / 1024 / 1024:.2f} MB uncompressed)")
    print(f"  [SUCCESS] Created {zip_path.name} ({zip_size / 1024 / 1024:.2f} MB compressed)")

    # Verify zip integrity
    with zipfile.ZipFile(zip_path, "r") as zipf:
        namelist = zipf.namelist()
        required_entries = [
            "backend/app.py",
            "backend/engine/audit_runner.py",
            "backend/tests/test_audit_engine.py",
            "frontend/src/App.tsx",
            "dataset/deletion_requests.csv",
            "evaluation/evaluation_report.md",
            "output.csv"
        ]
        for req in required_entries:
            if req not in namelist:
                print(f"  [WARN] Missing expected entry in zip: {req}")
            else:
                print(f"  Verified zip member: {req}")

    print("\nSubmission packaging complete! Ready for HackerRank submission.")

def main():
    validate_deliverables()
    create_zip()

if __name__ == "__main__":
    main()
