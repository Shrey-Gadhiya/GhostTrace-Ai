HEAD
# GhostTrace AI — Intelligent Data Deletion Audit Platform
### HackerRank Orchestrate October 2026 Submission: "Ghost Data Still Exists"
**Enterprise Privacy Compliance & Distributed Forensic Deletion Verification**

---

## 1. System Overview

**GhostTrace AI** is an evidence-driven, deterministic-first privacy compliance audit platform built for **Northstar Shop**. In distributed multi-tier enterprise architectures, customer data erasure requests (e.g. under GDPR Article 17 "Right to Erasure" and CCPA/CPRA) frequently fail silently. While customer portals or account microservices may log a workflow status as `COMPLETE`, lingering copies of customer personally identifiable information (PII) often remain in secondary search indices, active ETL sync streams, backup snapshots, or unredacted tombstones. These residual records represent **"Ghost Data"**.

GhostTrace AI performs an independent, ground-truth audit of customer deletion requests against distributed system states at the specified audit cutoff timestamp (`audit_at`).

### Core Capabilities
- **Grounded Multi-System Identity Resolution:** Resolves primary customer IDs, active emails, and historical aliases without unsafe transitive merging.
- **Multi-Format Evidence Extraction:** Safely parses and validates forensic evidence across JSON, CSV, Log files, and SQL snapshot exports with SHA-256 integrity verification.
- **Authoritative Policy Evaluation:** Enforces statutory rules from `deletion_rules.csv` differentiating `DELETE`, `REDACT`, `ANONYMIZE`, and `RETAIN` requirements.
- **Point-in-Time State Reconstruction:** Strictly evaluates resource states as of `audit_at` (rejecting post-audit operations as proof of deletion).
- **Active Data Flow & Restore Hazard Detection:** Identifies recurring synchronization pipelines and cold Glacier snapshots that can resurrect deleted customer data.
- **Authoritative Step Ordering & Validation:** Strictly adheres to the challenge specification's phase hierarchy, operation precedence, and ascending identifier ordering.

---

## 2. Architecture & Directory Structure

```
d:\orch hackthon project\
├── dataset/                         # Authoritative Northstar Shop forensic corpus
│   ├── deletion_requests.csv       # 518 customer deletion requests
│   ├── user_identities.csv         # 1,153 registered & historical identity links
│   ├── user_audit_log.csv          # 416 system audit timeline events
│   ├── deletion_rules.csv          # 8 statutory deletion policies
│   ├── evidence_files.csv          # 886 forensic evidence manifest entries
│   ├── sample_output.csv           # 20 canonical benchmark cases (100% concordance)
│   ├── output_template.csv         # Submission template (518 rows)
│   └── evidence/                   # Concrete forensic artifacts (JSON, LOG, SQL, CSV)
├── backend/                         # FastAPI & Core Python Audit Engine
│   ├── app.py                      # FastAPI application entrypoint with CORS
│   ├── config.py                   # Pydantic v2 application configuration
│   ├── engine/                     # Deterministic forensic audit pipeline
│   │   ├── loader.py               # Tabular dataset loading & schema validation
│   │   ├── identity_resolver.py    # Multi-system alias resolution
│   │   ├── evidence_extractor.py   # Multi-format parsers & SHA-256 validation
│   │   ├── policy_engine.py        # Authoritative rule enforcement
│   │   ├── state_reconstructor.py  # Point-in-time cutoff evaluation
│   │   ├── risk_detector.py        # Active sync & restore hazard detection
│   │   ├── decision_engine.py      # Status classification (COMPLETE/INCOMPLETE/NA)
│   │   ├── remediation_planner.py  # Ordered remediation actions generator
│   │   ├── step_ordering.py        # Authoritative phase & operation ordering
│   │   ├── validator.py            # Strict 15-operation & schema validator
│   │   └── csv_writer.py           # 3-column output.csv writer with round-trip check
│   ├── ai/                         # AI orchestration & token cost accounting
│   │   ├── provider.py             # Structured Pydantic parser & offline fallback
│   │   ├── prompts.py              # Version-controlled prompt templates
│   │   └── cost_tracker.py         # Token accounting ($0.00 offline default)
│   ├── api/                        # REST API routes (Overview, Cases, Systems, Runs, Eval, Exports)
│   ├── db/                         # SQLite application database & run ledger
│   └── tests/                      # Automated Pytest suite (19 test categories)
├── frontend/                        # High-Precision React/TypeScript/Tailwind UI
│   ├── src/
│   │   ├── App.tsx                 # Shell navigation & layout
│   │   ├── pages/                  # 8 functional operational pages
│   │   └── services/api.ts         # Typed REST client
│   ├── package.json
│   └── vite.config.ts
├── evaluation/                      # Measured evaluation reports
│   ├── evaluation_report.md        # Forensic accuracy & benchmark assessment
│   └── usage_report.md             # Token usage & cost accounting report
├── scripts/                         # CLI execution & packaging tools
│   ├── generate_dataset.py         # Reproducible forensic corpus generator
│   ├── run_audit.py                # Full 518-case audit runner
│   ├── evaluate.py                 # Benchmark & edge-case evaluator
│   └── package_submission.py       # Submission packaging & pre-flight checker
├── output.csv                       # Canonical 518-row challenge deliverable
├── requirements.txt                 # Backend Python dependencies
├── .env.example                     # Environment template
└── README.md                        # Documentation & setup guide
```

---

## 3. Authoritative Operations & Allowed States

The audit engine uses strictly the 15 authoritative operations and state mappings defined in `problem_statement.md`:

### Phase 1: `FINDINGS`
- `REPORT_ACTIVE_DATA_FLOW` with state `ACTIVE`
- `REPORT_RESTORE_RISK` with state `ACTIVE`
- `REPORT_REMAINING_RECORD` with state `PRESENT`
- `REPORT_EXPOSED_PII` with state `PRESENT`

### Phase 2: `REMEDIATION`
- `DISABLE_DATA_FLOW` with state `DISABLED` (evidence_id: `""`)
- `BLOCK_RESTORE` with state `BLOCKED` (evidence_id: `""`)
- `DELETE_RECORD` with state `ABSENT` (evidence_id: `""`)
- `REDACT_RECORD` with state `REDACTED` (evidence_id: `""`)
- `ANONYMIZE_RECORD` with state `ANONYMIZED` (evidence_id: `""`)

### Phase 3: `VERIFICATION`
- `VERIFY_DATA_FLOW_DISABLED` with state `DISABLED`
- `VERIFY_RESTORE_BLOCKED` with state `BLOCKED`
- `VERIFY_RECORD_ABSENT` with state `ABSENT`
- `VERIFY_RECORD_PRESENT` with state `PRESENT` (for policy-mandated fiscal retention)
- `VERIFY_RECORD_REDACTED` with state `REDACTED` (for account tombstones)
- `VERIFY_RECORD_ANONYMIZED` with state `ANONYMIZED`

---

## 4. Getting Started

### Prerequisites
- Python 3.11+ (Tested on Python 3.14.7)
- Node.js 18+ (Tested on Node v24.21.0 / npm 11.19.0)

### 1. Backend Installation & Startup
```powershell
# 1. Install backend dependencies
python -m pip install -r requirements.txt

# 2. Run automated test suite
python -m pytest backend/tests/ -v

# 3. Start FastAPI backend server
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```
The backend API and interactive OpenAPI documentation will be accessible at:
- **API Root:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`

### 2. Frontend Installation & Startup
```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install npm dependencies
npm install

# 3. Start Vite dev server
npm run dev
```
The React enterprise application will open at: `http://localhost:5173`

---

## 5. Running the Audit & Generating Deliverables

### Full Audit Execution via CLI
To execute the complete forensic audit across all 518 cases and generate `output.csv`:
```powershell
python scripts/run_audit.py
```
*Output:* Processes all 518 cases, produces validated `output.csv`, and records execution run in SQLite.

### Running Automated Evaluation & Reports
To evaluate accuracy against `sample_output.csv` and generate Markdown reports:
```powershell
python scripts/evaluate.py
```
*Output:*
- `evaluation/evaluation_report.md`
- `evaluation/usage_report.md`

### Building the Final Submission Bundle
To run pre-flight integrity checks and package `code.zip`:
```powershell
python scripts/package_submission.py
```
*Output:* Produces clean `code.zip` containing all code, tests, docs, dataset, and `output.csv` without unnecessary node_modules or secrets.

---

## 6. Measured Benchmark Results

- **Sample Benchmark Status Accuracy:** **100.0%** (20/20)
- **Exact Step JSON Match Accuracy:** **100.0%** (20/20)
- **Field-Level Match Accuracy:** **100.0%** (481/481)
- **Strict Sequence Accuracy:** **100.0%** (20/20)
- **Total Cases Processed:** **518**
- **Automated Pytest Tests:** **20 passed** (100% pass rate)

---

## 7. Author

**Made by Shrey Gadhiya**  
*HackerRank Orchestrate October 2026: "Ghost Data Still Exists"*

# GhostTrace-Ai
 0e1b76c3e62835e400b99eff955eb409fe2988c6
