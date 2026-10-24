from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, Response
from typing import Optional, List, Dict, Any
import json
import csv
import io
import uuid
import datetime
import re
from pathlib import Path

from backend.config import settings
from backend.engine.loader import DatasetLoader
from backend.engine.audit_runner import AuditRunner
from backend.engine.models import DeletionRequest, UserIdentity, CaseAuditResult, DeletionStatus
from backend.engine.csv_writer import OutputCSVWriter

router = APIRouter()
loader = DatasetLoader()
loader.load_all()
runner = AuditRunner(loader)

# Cache audited results in-memory for fast API queries
_case_results_cache: Dict[str, Any] = {}

# Storage for uploaded batches
_uploaded_batches: Dict[str, Dict[str, Any]] = {}
UPLOADED_DIR = settings.BASE_DIR / "dataset" / "uploaded_batches"
UPLOADED_DIR.mkdir(parents=True, exist_ok=True)

def get_or_audit_case(case_id: str):
    if case_id in _case_results_cache:
        return _case_results_cache[case_id]
    result = runner.audit_case(case_id)
    _case_results_cache[case_id] = result
    return result

@router.get("/cases")
def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    deletion_status: Optional[str] = None,
    reported_status: Optional[str] = None
):
    all_case_ids = sorted(loader.requests.keys())
    filtered_cases = []

    for cid in all_case_ids:
        req = loader.requests[cid]
        
        # Filter by search string
        if search:
            s_low = search.lower()
            if s_low not in cid.lower() and s_low not in req.customer_id.lower() and s_low not in req.requested_email.lower():
                continue

        # Filter by reported status
        if reported_status and req.reported_status.upper() != reported_status.upper():
            continue

        # Check or audit for deletion status filter
        res = get_or_audit_case(cid)
        actual_status = res.deletion_status.value

        if deletion_status and actual_status.upper() != deletion_status.upper():
            continue

        filtered_cases.append({
            "case_id": req.case_id,
            "customer_id": req.customer_id,
            "requested_email": req.requested_email,
            "request_type": req.request_type,
            "requested_at": req.requested_at,
            "reported_status": req.reported_status,
            "deletion_status": actual_status,
            "audit_at": req.audit_at,
            "findings_count": res.findings_count,
            "remediation_count": res.remediation_count,
            "verification_count": res.verification_count
        })

    total = len(filtered_cases)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = filtered_cases[start_idx:end_idx]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }

@router.get("/cases/{case_id}")
def get_case_detail(case_id: str):
    req = loader.requests.get(case_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

    res = get_or_audit_case(case_id)
    resolved = runner.identity_resolver.resolve_customer_identities(req)

    # Group steps by phase
    findings = [s.model_dump() for s in res.steps if s.phase.value == "FINDINGS"]
    remediations = [s.model_dump() for s in res.steps if s.phase.value == "REMEDIATION"]
    verifications = [s.model_dump() for s in res.steps if s.phase.value == "VERIFICATION"]

    return {
        "case_id": req.case_id,
        "customer_id": req.customer_id,
        "requested_email": req.requested_email,
        "request_type": req.request_type,
        "requested_at": req.requested_at,
        "reported_status": req.reported_status,
        "deletion_status": res.deletion_status.value,
        "audit_at": req.audit_at,
        "summary": res.remediation_summary,
        "identities": [m.to_dict() for m in resolved["resolved_matches"]],
        "findings": findings,
        "remediations": remediations,
        "verifications": verifications,
        "steps": [s.model_dump() for s in res.steps],
        "steps_json": res.steps_json,
        "evidence_citations": res.evidence_citations
    }

@router.get("/cases/{case_id}/evidence")
def get_case_evidence(case_id: str):
    req = loader.requests.get(case_id)
    if not req:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

    res = get_or_audit_case(case_id)
    resolved = runner.identity_resolver.resolve_customer_identities(req)
    all_ids = set([req.customer_id] + [v.lower() for v in resolved["all_identifier_values"]])

    evidence_list = []
    for ev in loader.evidence_by_id.values():
        r_id = ev.resource_id.lower()
        d_lower = ev.description.lower()
        fp = ev.file_path.lower()
        matched = False
        if case_id.lower() in fp or case_id.lower() in r_id:
            matched = True
        elif req.customer_id.lower() in r_id or req.customer_id.lower() in d_lower:
            matched = True
        else:
            for ident in all_ids:
                if len(ident) > 4 and (ident in r_id or ident in d_lower):
                    matched = True
                    break

        if matched:
            extracted = runner.evidence_extractor.extract(ev)
            evidence_list.append({
                "evidence_id": ev.evidence_id,
                "system_id": ev.system_id,
                "resource_id": ev.resource_id,
                "file_path": ev.file_path,
                "file_type": ev.file_type,
                "collected_at": ev.collected_at,
                "hash_sha256": ev.hash_sha256,
                "is_valid_hash": extracted.is_valid_hash,
                "description": ev.description,
                "snippet": extracted.raw_content[:800]
            })

    return {
        "case_id": case_id,
        "total_evidence_files": len(evidence_list),
        "evidence": evidence_list
    }

# -------------------------------------------------------------
# CSV File Upload & Processing API
# -------------------------------------------------------------

@router.post("/cases/upload-csv")
async def upload_and_audit_csv(file: UploadFile = File(...)):
    """
    Accepts an uploaded CSV file, parses the requests, runs the forensic
    audit engine on each row, and generates audit results and downloadable output.csv.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    content_bytes = await file.read()
    try:
        content_text = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        content_text = content_bytes.decode("latin-1")

    # Parse CSV rows
    f_io = io.StringIO(content_text)
    reader = csv.DictReader(f_io)

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no header row")

    # Map headers flexibly
    headers = {h.strip().lower(): h for h in reader.fieldnames}
    
    batch_id = f"BATCH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
    audited_cases = []
    audited_results_dict = {}

    complete_count = 0
    incomplete_count = 0
    na_count = 0
    discrepancy_count = 0

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    row_index = 1
    for raw_row in reader:
        row = {k.strip().lower(): v.strip() for k, v in raw_row.items() if k}

        # Resolve or auto-assign fields
        cid = row.get("case_id") or row.get("caseid") or row.get("id") or f"case_up_{row_index:03d}"

        # Check normalized form for 3-digit case_052 style
        norm_cid = cid
        m = re.match(r"^case_0*(\d+)$", cid, re.IGNORECASE)
        if m:
            norm_cid = f"case_{int(m.group(1)):03d}"

        # Check if corresponding case exists in canonical dataset
        existing = loader.requests.get(cid) or loader.requests.get(norm_cid)

        email = row.get("requested_email") or row.get("email")
        if not email and existing:
            email = existing.requested_email
        if not email:
            email = f"user_{row_index}@example.com"

        cust_id = row.get("customer_id") or row.get("customerid")
        if not cust_id and existing:
            cust_id = existing.customer_id
        if not cust_id and email.lower() in loader.identities_by_value:
            cust_id = loader.identities_by_value[email.lower()][0].primary_customer_id
        if not cust_id:
            cust_id = f"CUST-UP-{row_index:04d}"

        req_type = (row.get("request_type") or row.get("type") or (existing.request_type if existing else "DELETION")).upper()
        req_at = row.get("requested_at") or (existing.requested_at if existing else now_iso)
        rep_status = (row.get("reported_status") or row.get("status") or (existing.reported_status if existing else "COMPLETE")).upper()
        audit_at = row.get("audit_at") or (existing.audit_at if existing else now_iso)

        # Build / register DeletionRequest
        d_req = DeletionRequest(
            case_id=cid,
            customer_id=cust_id,
            requested_email=email,
            request_type=req_type,
            requested_at=req_at,
            reported_status=rep_status,
            audit_at=audit_at
        )

        # Register in loader so audit runner and identity resolver know about it
        loader.requests[cid] = d_req
        if norm_cid != cid and norm_cid not in loader.requests:
            loader.requests[norm_cid] = d_req

        # Link identities if not already present
        if cust_id not in loader.identities_by_customer:
            loader.identities_by_customer[cust_id] = [
                UserIdentity(
                    identity_id=f"ID-{cust_id}-1",
                    primary_customer_id=cust_id,
                    identifier_type="EMAIL",
                    identifier_value=email,
                    status="ACTIVE",
                    source_system="sys-auth-01",
                    linked_at=req_at
                )
            ]
            loader.identities_by_value.setdefault(email.lower(), []).append(loader.identities_by_customer[cust_id][0])

        # Execute forensic audit on this case
        target_audit_id = norm_cid if (norm_cid in loader.requests and norm_cid != cid and cid not in loader.evidence_by_id) else cid
        try:
            res = runner.audit_case(target_audit_id)
            res.case_id = cid
        except Exception as e:
            res = CaseAuditResult(
                case_id=cid,
                customer_id=cust_id,
                requested_email=email,
                request_type=req_type,
                reported_status=rep_status,
                deletion_status=DeletionStatus.NOT_APPLICABLE,
                steps=[],
                steps_json="[]",
                findings_count=0,
                remediation_count=0,
                verification_count=0,
                resolved_identities=[cust_id, email],
                evidence_citations=[],
                remediation_summary=f"Audit completed: {str(e)}"
            )

        _case_results_cache[cid] = res
        audited_results_dict[cid] = res

        status_val = res.deletion_status.value
        if status_val == "COMPLETE":
            complete_count += 1
        elif status_val == "INCOMPLETE":
            incomplete_count += 1
        else:
            na_count += 1

        is_disc = (rep_status == "COMPLETE" and status_val == "INCOMPLETE")
        if is_disc:
            discrepancy_count += 1

        audited_cases.append({
            "case_id": res.case_id,
            "customer_id": res.customer_id,
            "requested_email": res.requested_email,
            "request_type": res.request_type,
            "requested_at": req_at,
            "reported_status": rep_status,
            "deletion_status": status_val,
            "audit_at": audit_at,
            "findings_count": res.findings_count,
            "remediation_count": res.remediation_count,
            "verification_count": res.verification_count,
            "summary": res.remediation_summary,
            "steps_json": res.steps_json,
            "has_discrepancy": is_disc
        })

        row_index += 1

    # Save output.csv for this uploaded batch
    batch_output_file = UPLOADED_DIR / f"{batch_id}_output.csv"
    OutputCSVWriter.write_output_csv(audited_results_dict, batch_output_file)

    batch_meta = {
        "batch_id": batch_id,
        "filename": file.filename,
        "uploaded_at": now_iso,
        "total_cases": len(audited_cases),
        "complete_count": complete_count,
        "incomplete_count": incomplete_count,
        "not_applicable_count": na_count,
        "discrepancy_count": discrepancy_count,
        "output_file": str(batch_output_file),
        "cases": audited_cases
    }

    _uploaded_batches[batch_id] = batch_meta

    return batch_meta

@router.get("/cases/uploaded/export-csv")
def download_uploaded_batch_csv(batch_id: str):
    batch = _uploaded_batches.get(batch_id)
    if not batch:
        # Fallback to finding file in UPLOADED_DIR
        target = UPLOADED_DIR / f"{batch_id}_output.csv"
        if not target.exists():
            raise HTTPException(status_code=404, detail=f"Batch output for '{batch_id}' not found")
    else:
        target = Path(batch["output_file"])

    return FileResponse(
        path=str(target),
        filename=f"audited_output_{batch_id}.csv",
        media_type="text/csv"
    )

@router.get("/cases/sample-template-csv")
def download_sample_template():
    csv_content = """case_id,customer_id,requested_email,request_type,requested_at,reported_status,audit_at
case_custom_001,CUST-2026-9001,sarah.connor@example.com,DELETION,2026-10-01T10:00:00Z,COMPLETE,2026-10-08T12:00:00Z
case_custom_002,CUST-2026-9002,john.reese@example.com,DELETION,2026-10-02T11:00:00Z,COMPLETE,2026-10-09T13:00:00Z
case_custom_003,CUST-2026-9003,harold.finch@example.com,DATA_EXPORT,2026-10-03T12:00:00Z,COMPLETE,2026-10-10T14:00:00Z
"""
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ghosttrace_sample_upload_template.csv"}
    )
