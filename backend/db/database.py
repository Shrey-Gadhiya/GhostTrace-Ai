import sqlite3
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.config import settings

def get_db_connection() -> sqlite3.Connection:
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_runs (
        run_id TEXT PRIMARY KEY,
        dataset_fingerprint TEXT,
        started_at TEXT,
        completed_at TEXT,
        status TEXT,
        total_cases INTEGER,
        complete_cases INTEGER,
        incomplete_cases INTEGER,
        not_applicable_cases INTEGER,
        error_count INTEGER,
        model_provider TEXT,
        model_identifier TEXT,
        total_tokens INTEGER,
        estimated_cost_usd REAL,
        output_file TEXT,
        logs TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_cache (
        run_id TEXT,
        case_id TEXT,
        customer_id TEXT,
        requested_email TEXT,
        request_type TEXT,
        reported_status TEXT,
        deletion_status TEXT,
        findings_count INTEGER,
        remediation_count INTEGER,
        verification_count INTEGER,
        steps_json TEXT,
        summary TEXT,
        PRIMARY KEY (run_id, case_id)
    )
    """)

    conn.commit()
    conn.close()

def save_analysis_run(run_data: Dict[str, Any], case_results: Optional[List[Dict[str, Any]]] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO analysis_runs (
        run_id, dataset_fingerprint, started_at, completed_at, status,
        total_cases, complete_cases, incomplete_cases, not_applicable_cases, error_count,
        model_provider, model_identifier, total_tokens, estimated_cost_usd, output_file, logs
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_data["run_id"],
        run_data.get("dataset_fingerprint", ""),
        run_data["started_at"],
        run_data["completed_at"],
        run_data["status"],
        run_data["total_cases"],
        run_data["complete_cases"],
        run_data["incomplete_cases"],
        run_data["not_applicable_cases"],
        run_data["error_count"],
        run_data.get("model_provider", "deterministic"),
        run_data.get("model_identifier", "rules_engine"),
        run_data.get("total_tokens", 0),
        run_data.get("estimated_cost_usd", 0.0),
        run_data.get("output_file", ""),
        run_data.get("logs", "")
    ))

    if case_results:
        for c in case_results:
            cursor.execute("""
            INSERT OR REPLACE INTO case_cache (
                run_id, case_id, customer_id, requested_email, request_type,
                reported_status, deletion_status, findings_count, remediation_count,
                verification_count, steps_json, summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_data["run_id"],
                c["case_id"],
                c["customer_id"],
                c["requested_email"],
                c["request_type"],
                c["reported_status"],
                c["deletion_status"],
                c.get("findings_count", 0),
                c.get("remediation_count", 0),
                c.get("verification_count", 0),
                c.get("steps_json", "[]"),
                c.get("remediation_summary", "")
            ))

    conn.commit()
    conn.close()

def get_runs() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_runs ORDER BY started_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_run_by_id(run_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_runs WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_latest_run() -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_runs WHERE status = 'COMPLETED' ORDER BY completed_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Initialize on import
init_db()
