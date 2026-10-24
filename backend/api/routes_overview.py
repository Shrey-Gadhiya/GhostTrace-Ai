from fastapi import APIRouter
from typing import Dict, Any
from backend.engine.loader import DatasetLoader
from backend.db.database import get_latest_run, get_runs

router = APIRouter()
loader = DatasetLoader()
loader.load_all()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GhostTrace AI",
        "dataset_loaded": loader._is_loaded,
        "total_cases": len(loader.requests)
    }

@router.get("/overview")
def get_overview_metrics():
    latest_run = get_latest_run()
    total_requests = len(loader.requests)
    
    # If a run has been performed, read actual counts from latest run
    if latest_run:
        audited_count = latest_run["total_cases"]
        complete_count = latest_run["complete_cases"]
        incomplete_count = latest_run["incomplete_cases"]
        na_count = latest_run["not_applicable_cases"]
        run_id = latest_run["run_id"]
        run_status = latest_run["status"]
        last_run_time = latest_run["completed_at"]
    else:
        # Pre-run counts
        audited_count = 0
        complete_count = 0
        incomplete_count = 0
        na_count = 0
        run_id = None
        run_status = "AWAITING_FIRST_RUN"
        last_run_time = None

    # System breakdown
    systems_data = [
        {"system_id": "sys-auth-01", "name": "Authentication & Accounts", "type": "SQL Store", "risks": "Tombstones, Credential Purge"},
        {"system_id": "sys-crm-01", "name": "Customer Relationship Mgmt", "type": "CRM SaaS", "risks": "Sales Leads, Historical Aliases"},
        {"system_id": "sys-search-es", "name": "Elasticsearch Search Index", "type": "Search Cluster", "risks": "De-indexing Lag"},
        {"system_id": "sys-orders-db", "name": "Order & Transactions", "type": "SQL Store", "risks": "Fiscal 7yr Retain vs PII Redact"},
        {"system_id": "sys-marketing-mail", "name": "Outbound Marketing Mailer", "type": "Mailing Engine", "risks": "Mailing List Lingering"},
        {"system_id": "sys-lake-analytics", "name": "Analytics Data Lake", "type": "Data Lake", "risks": "Pseudonymization Gaps"},
        {"system_id": "sys-sync-worker", "name": "Active ETL / CDC Sync Workers", "type": "Sync Pipeline", "risks": "Active Data Resurrections"},
        {"system_id": "sys-backup-s3", "name": "Backup Cold Snapshots", "type": "S3 Glacier", "risks": "Unblocked Restore Risks"}
    ]

    return {
        "total_requests": total_requests,
        "audited_count": audited_count,
        "complete_count": complete_count,
        "incomplete_count": incomplete_count,
        "not_applicable_count": na_count,
        "pending_count": total_requests - audited_count,
        "latest_run": {
            "run_id": run_id,
            "status": run_status,
            "completed_at": last_run_time
        },
        "systems_summary": systems_data,
        "rules_count": len(loader.rules_by_id),
        "evidence_count": len(loader.evidence_by_id)
    }
