#!/usr/bin/env python3
"""
GhostTrace AI — Full Corpus Audit CLI
Runs the forensic audit across all 518 cases and generates output.csv.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings
from backend.engine.loader import DatasetLoader
from backend.engine.audit_runner import AuditRunner
from backend.engine.csv_writer import OutputCSVWriter
from backend.ai.cost_tracker import tracker
from backend.db.database import save_analysis_run
import uuid
import datetime

def main():
    print("=" * 70)
    print("  GhostTrace AI — Intelligent Data Deletion Audit Platform")
    print("  HackerRank Orchestrate October 2026: 'Ghost Data Still Exists'")
    print("=" * 70)

    start_time = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.time()

    print(f"Loading dataset from: {settings.DATASET_DIR}")
    loader = DatasetLoader(settings.DATASET_DIR)
    loader.load_all()
    print(f"Loaded {len(loader.requests)} deletion requests.")
    print(f"Loaded {len(loader.evidence_by_id)} forensic evidence files.")
    print(f"Loaded {len(loader.rules_by_id)} statutory deletion rules.")

    print("\nExecuting forensic audit pipeline across all cases...")
    runner = AuditRunner(loader)
    results = {}
    
    complete = 0
    incomplete = 0
    na = 0
    cached_cases = []

    for idx, (cid, req) in enumerate(sorted(loader.requests.items()), start=1):
        res = runner.audit_case(cid)
        results[cid] = res
        cached_cases.append(res.model_dump())
        
        status_str = res.deletion_status.value
        if status_str == "COMPLETE":
            complete += 1
        elif status_str == "INCOMPLETE":
            incomplete += 1
        else:
            na += 1

        if idx % 100 == 0 or idx == len(loader.requests):
            print(f"  Processed {idx}/{len(loader.requests)} cases...")

    elapsed = time.time() - t0
    end_time = datetime.datetime.now(datetime.timezone.utc)

    print("\nAudit Determination Summary:")
    print(f"  - Verified COMPLETE:        {complete}")
    print(f"  - INCOMPLETE (Ghost Data):  {incomplete}")
    print(f"  - NOT_APPLICABLE:           {na}")
    print(f"  - Total Processed:          {len(results)}")
    print(f"  - Elapsed Time:             {elapsed:.2f}s")

    print(f"\nWriting authoritative challenge output: {settings.OUTPUT_FILE}")
    out_path = OutputCSVWriter.write_output_csv(results, settings.OUTPUT_FILE)
    verified_rows = OutputCSVWriter.validate_roundtrip(out_path, expected_count=len(loader.requests))
    print(f"  [SUCCESS] {out_path.name} verified with {verified_rows} rows.")

    # Record run in SQLite DB
    run_id = f"RUN-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    cost_summary = tracker.get_summary()

    run_record = {
        "run_id": run_id,
        "dataset_fingerprint": f"sha256-dataset-{len(loader.requests)}-{len(loader.evidence_by_id)}",
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "status": "COMPLETED",
        "total_cases": len(results),
        "complete_cases": complete,
        "incomplete_cases": incomplete,
        "not_applicable_cases": na,
        "error_count": 0,
        "model_provider": settings.LLM_PROVIDER,
        "model_identifier": settings.LLM_MODEL,
        "total_tokens": cost_summary.get("total_tokens", 0),
        "estimated_cost_usd": cost_summary.get("total_cost_usd", 0.0),
        "output_file": str(out_path),
        "logs": f"CLI Audit execution completed in {elapsed:.2f}s."
    }
    save_analysis_run(run_record, cached_cases)
    print(f"  [SUCCESS] Persisted audit run {run_id} to {settings.DB_PATH}")

if __name__ == "__main__":
    main()
