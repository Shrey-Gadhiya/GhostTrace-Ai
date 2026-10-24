from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import datetime
import uuid
from backend.config import settings
from backend.engine.loader import DatasetLoader
from backend.engine.audit_runner import AuditRunner
from backend.engine.csv_writer import OutputCSVWriter
from backend.ai.cost_tracker import tracker
from backend.db.database import save_analysis_run, get_runs, get_run_by_id

router = APIRouter()
loader = DatasetLoader()
loader.load_all()

@router.post("/runs")
def trigger_analysis_run():
    run_id = f"RUN-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    start_time = datetime.datetime.now(datetime.timezone.utc)
    
    logs = []
    logs.append(f"[{start_time.isoformat()}] Starting GhostTrace AI analysis run {run_id}")
    logs.append(f"[{start_time.isoformat()}] Loaded {len(loader.requests)} cases from {settings.DATASET_DIR}")
    
    runner = AuditRunner(loader)
    results = {}
    
    complete_count = 0
    incomplete_count = 0
    na_count = 0
    errors = 0
    cached_cases = []

    for cid in sorted(loader.requests.keys()):
        try:
            res = runner.audit_case(cid)
            results[cid] = res
            status_val = res.deletion_status.value
            if status_val == "COMPLETE":
                complete_count += 1
            elif status_val == "INCOMPLETE":
                incomplete_count += 1
            else:
                na_count += 1

            cached_cases.append(res.model_dump())
        except Exception as e:
            errors += 1
            logs.append(f"ERROR processing case {cid}: {str(e)}")

    # Write output.csv
    output_path = OutputCSVWriter.write_output_csv(results, settings.OUTPUT_FILE)
    logs.append(f"Generated compliant output CSV at {output_path} with {len(results)} rows.")

    end_time = datetime.datetime.now(datetime.timezone.utc)
    logs.append(f"[{end_time.isoformat()}] Completed analysis run. Duration: {(end_time - start_time).total_seconds():.2f}s")

    cost_summary = tracker.get_summary()

    run_record = {
        "run_id": run_id,
        "dataset_fingerprint": f"sha256-dataset-{len(loader.requests)}-{len(loader.evidence_by_id)}",
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "status": "COMPLETED" if errors == 0 else "PARTIAL_FAILURE",
        "total_cases": len(results),
        "complete_cases": complete_count,
        "incomplete_cases": incomplete_count,
        "not_applicable_cases": na_count,
        "error_count": errors,
        "model_provider": settings.LLM_PROVIDER,
        "model_identifier": settings.LLM_MODEL,
        "total_tokens": cost_summary.get("total_tokens", 0),
        "estimated_cost_usd": cost_summary.get("total_cost_usd", 0.0),
        "output_file": str(output_path),
        "logs": "\n".join(logs)
    }

    save_analysis_run(run_record, cached_cases)
    return run_record

@router.get("/runs")
def list_analysis_runs():
    return {"runs": get_runs()}

@router.get("/runs/{run_id}")
def get_analysis_run(run_id: str):
    run = get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run

@router.get("/runs/{run_id}/logs")
def get_run_logs(run_id: str):
    run = get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return {"run_id": run_id, "logs": run.get("logs", "")}
