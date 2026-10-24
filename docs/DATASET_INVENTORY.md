# Northstar Shop: Dataset & Evidence Inventory
## HackerRank Orchestrate October 2026 — Ghost Data Still Exists
### Authoritative Audit Protocol & Evidence Mapping

---

### 1. Dataset Schema Manifest

#### `dataset/deletion_requests.csv`
- Primary table of customer deletion requests.
- Row Count: 518 cases (`case_001` through `case_518`).
- Schema:
  * `case_id` (string, primary key): e.g., `case_001`
  * `customer_id` (string): Master customer code, e.g., `CUST-2026-1001`
  * `requested_email` (string): Email provided at time of request
  * `request_type` (string): `DELETION` or non-deletion (`DATA_EXPORT`, `ACCOUNT_INQUIRY`, `PASSWORD_RESET`)
  * `requested_at` (ISO 8601 UTC timestamp): e.g., `2026-10-01T09:00:00Z`
  * `reported_status` (string): Status claimed by internal workflow (`COMPLETE`, `IN_PROGRESS`, `PENDING`)
  * `audit_at` (ISO 8601 UTC timestamp): Evaluation cutoff point, e.g., `2026-10-08T11:00:00Z`

#### `dataset/user_identities.csv`
- Multi-system linked customer identities, historical aliases, and devices.
- Row Count: 1,153 identity links.
- Schema:
  * `identity_id` (string, unique link identifier): e.g., `ID-CUST-2026-1001-1`
  * `primary_customer_id` (string): Linked master customer UUID
  * `identifier_type` (string): `EMAIL`, `INTERNAL_ID`, `PHONE`, `DEVICE_ID`, `IP_ADDRESS`
  * `identifier_value` (string): Canonical identity value
  * `status` (string): `ACTIVE`, `HISTORICAL_ALIAS`, `UNVERIFIED_MERGE`
  * `source_system` (string): Originating system (e.g., `sys-auth-01`, `sys-crm-01`)
  * `linked_at` (ISO 8601 UTC timestamp)

#### `dataset/user_audit_log.csv`
- Chronological system event log tracking deletions, sync jobs, and exports.
- Row Count: 416 events.
- Schema:
  * `log_id` (string): Event ID
  * `system_id` (string): System logging the event
  * `resource_id` (string): Target resource identifier
  * `event_type` (string): `DELETION_REQUESTED`, `EXPORT_REQUESTED`, `RECORD_DELETED`, `DATA_SYNC_JOB`
  * `actor` (string): Requesting actor or service account
  * `timestamp` (ISO 8601 UTC timestamp)
  * `details` (JSON string): Additional event context

#### `dataset/deletion_rules.csv`
- Authoritative enterprise deletion policy rules.
- Row Count: 8 rules.
- Schema:
  * `rule_id`: e.g., `RULE_AUTH_PURGE`, `RULE_AUTH_TOMBSTONE`, `RULE_ORDER_FISCAL`
  * `system_id`: Applicable system (`sys-auth-01`, `sys-crm-01`, `sys-search-es`, `sys-orders-db`, `sys-marketing-mail`, `sys-lake-analytics`, `sys-backup-s3`)
  * `data_category`: Category of data under evaluation
  * `required_treatment`: `DELETE`, `REDACT`, `ANONYMIZE`, `RETAIN`
  * `retention_rationale`: Statutory justification (GDPR Art. 17, Fiscal Tax Code 7yr mandatory retention)
  * `prohibited_fields`: Comma-separated list of prohibited direct identifiers
  * `allowed_fields`: Comma-separated list of permitted fields

#### `dataset/evidence_files.csv`
- Forensics manifest of evidence artifacts collected as of `audit_at`.
- Row Count: 886 evidence records.
- Schema:
  * `evidence_id`: Canonical reference ID (e.g., `EV-AUTH-001`, `EV-ES-002`, `EV-SYNC-003`)
  * `system_id`: Originating system ID
  * `resource_id`: Target resource or document ID
  * `file_path`: Relative file path under `dataset/evidence/`
  * `file_type`: `JSON`, `LOG`, `SQL`, `CSV`, `PDF`, `IMAGE`
  * `collected_at`: Collection timestamp
  * `hash_sha256`: Cryptographic SHA-256 integrity hash
  * `description`: Detailed forensic summary

#### `dataset/sample_output.csv`
- Canonical ground-truth benchmark output for `case_001` through `case_020`.
- Format: `case_id`, `deletion_status`, `steps_json`

#### `dataset/output_template.csv`
- Blank template for all 518 cases with columns `case_id`, `deletion_status`, `steps_json`.

---

### 2. Forensic Evidence Storage Inventory (`dataset/evidence/`)
- `evidence/json/`: Elasticsearch query outputs (`es_search_case_XXX.json`), authentication tombstones (`auth_case_XXX.json`), Glacier backup snapshot metadata (`backup_meta_case_XXX.json`).
- `evidence/logs/`: CRM purge execution logs (`crm_purge_case_XXX.log`), ETL sync worker logs (`sync_worker_case_XXX.log`).
- `evidence/sql/`: SQLite / SQL table dumps of fiscal orders (`orders_case_XXX.sql`).
- `evidence/csv/`: Flat files of CRM sales leads with historical aliases (`crm_leads_case_XXX.csv`), newsletter subscriptions (`mail_list_case_XXX.csv`).
- `evidence/pdf/`: Invoices and compliance audit reports.
- `evidence/images/`: Identity verification screenshots and signed delivery receipts.
