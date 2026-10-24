# GhostTrace AI — Implementation Plan & Requirements Traceability
## HackerRank Orchestrate October 2026: "Ghost Data Still Exists"

### 1. Architectural Architecture & Component Separation
GhostTrace AI operates on an evidence-driven, deterministic-first privacy audit pipeline:

```
[ Dataset Files ]
       |
       v
+---------------------------------------------------------------------------------+
| backend/engine/loader.py (Strict CSV/manifest schema validation)                |
+---------------------------------------------------------------------------------+
       |
       +---> [ backend/engine/identity_resolver.py ]
       |     - Primary customer ID + active & historical aliases
       |     - Disallows unsafe transitive matching
       |
       +---> [ backend/engine/evidence_extractor.py ]
       |     - Multi-format parsers (JSON, CSV, Log regex, SQL snapshots, Image/PDF)
       |     - SHA-256 verification and path traversal containment
       |
       +---> [ backend/engine/policy_engine.py ]
       |     - Evaluates rules from deletion_rules.csv
       |     - Differentiates DELETE, REDACT, ANONYMIZE, and RETAIN requirements
       |
       +---> [ backend/engine/state_reconstructor.py ]
       |     - Evaluates resource presence/absence strictly as of audit_at
       |     - Out-of-order & post-audit event handling
       |
       +---> [ backend/engine/risk_detector.py ]
       |     - Active sync pipeline / ETL resurrection risk detection
       |     - Backup snapshot restore hazard detection
       |
       +---> [ backend/engine/decision_engine.py ]
       |     - Canonical classification: COMPLETE | INCOMPLETE | NOT_APPLICABLE
       |
       +---> [ backend/engine/remediation_planner.py & step_ordering.py ]
       |     - Strict operation prioritization & ascending system_id/resource_id
       |     - Step sequence numbering from 1..N
       |
       v
[ backend/engine/csv_writer.py & validator.py ]
       |
       +---> output.csv (Strict 3-column CSV with valid steps_json)
```

---

### 2. Requirements Traceability Matrix

| Requirement | Implementation Module | Automated Tests |
|---|---|---|
| Exact 518 cases processing | `backend/engine/loader.py` | `test_full_dataset_row_count` |
| Identity alias resolution | `backend/engine/identity_resolver.py` | `test_identity_historical_aliases` |
| Multi-format evidence extraction | `backend/engine/evidence_extractor.py` | `test_evidence_extraction_formats` |
| Authoritative policy evaluation | `backend/engine/policy_engine.py` | `test_policy_rules_enforcement` |
| State reconstruction as of `audit_at` | `backend/engine/state_reconstructor.py` | `test_point_in_time_audit_cutoff` |
| Active data-flow & restore risks | `backend/engine/risk_detector.py` | `test_active_flow_and_restore_risk` |
| Tombstone PII stripping | `backend/engine/policy_engine.py` | `test_tombstone_redaction_vs_exposure` |
| Fiscal retention preservation | `backend/engine/policy_engine.py` | `test_retained_fiscal_orders` |
| Canonical status classification | `backend/engine/decision_engine.py` | `test_classification_semantics` |
| Authoritative 15 operations & states | `backend/engine/validator.py` | `test_allowed_operations_and_states` |
| Step ordering & sequence | `backend/engine/step_ordering.py` | `test_step_phase_and_op_ordering` |
| Benchmark comparison against samples | `backend/eval/evaluator.py` | `test_benchmark_sample_output_match` |
| FastAPI REST API Endpoints | `backend/api/` | `test_api_endpoints` |
| React Enterprise Web Application | `frontend/src/` | Frontend build & test |
| Submission deliverables generation | `scripts/package_submission.py` | `test_submission_bundle` |

---

### 3. Implementation Checklist & Progress

- [x] Phase 1: Problem inspection, dataset schema formalization, and dataset generator.
- [ ] Phase 2: Core Python Audit Engine (`backend/engine/`).
- [ ] Phase 3: AI orchestration, prompts, cost tracker, and deterministic fallback.
- [ ] Phase 4: Enterprise FastAPI Backend API (`backend/api/`).
- [ ] Phase 5: High-Precision React/Tailwind Frontend (`frontend/`).
- [ ] Phase 6: Automated Pytest Suite covering all 18 test categories.
- [ ] Phase 7: Full dataset execution and output validation for all 518 cases.
- [ ] Phase 8: Deliverables generation (`output.csv`, `evaluation_report.md`, `usage_report.md`, `code.zip`).
