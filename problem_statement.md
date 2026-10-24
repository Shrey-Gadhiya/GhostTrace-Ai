# HackerRank Orchestrate — October 2026 Challenge: "Ghost Data Still Exists"
## Challenge Specification & Audit Protocol

### Overview
In distributed multi-tier enterprise architectures such as **Northstar Shop**, customer data erasure requests (e.g. under GDPR Article 17 "Right to Erasure" and CCPA/CPRA) frequently fail silently. While a customer-facing support portal or account microservice may log a workflow status as `COMPLETE`, lingering copies of customer personally identifiable information (PII) often remain in search indices, backup snapshots, analytical data lakes, third-party synchronization streams, or secondary cache stores. These residual records represent **"Ghost Data"**.

**GhostTrace AI** is designed to perform an independent, evidence-grounded audit of customer deletion requests against distributed system states at the specified audit timestamp (`audit_at`).

---

### Authoritative Operations & Allowed States

#### 1. FINDING Operations (Phase: `FINDINGS`)
Used when an audit reveals non-compliance, active replication risks, or un-remediated records.
- `REPORT_REMAINING_RECORD` with state `PRESENT`: A record that should have been deleted, redacted, or anonymized according to policy is still present in the system.
- `REPORT_EXPOSED_PII` with state `PRESENT`: Direct or sensitive PII fields are exposed in tombstones, logs, or unredacted metadata.
- `REPORT_ACTIVE_DATA_FLOW` with state `ACTIVE`: An automated replication, sync pipeline, or ETL job is actively running and capable of resurrecting deleted data into target datastores.
- `REPORT_RESTORE_RISK` with state `ACTIVE`: A point-in-time restore path, unpurged WAL log, or snapshot exists that can restore deleted customer data without exclusion filters.

#### 2. REMEDIATION Operations (Phase: `REMEDIATION`)
Used to specify the exact sequence of actions required to bring the system into full compliance.
- `DISABLE_DATA_FLOW` with state `DISABLED`: Terminate or pause the active sync/ETL pipeline before modifying data.
- `BLOCK_RESTORE` with state `BLOCKED`: Tag or filter backup snapshots/WAL logs to prevent restoring deleted customer records.
- `DELETE_RECORD` with state `ABSENT`: Permanently drop or purge the record from the datastore.
- `REDACT_RECORD` with state `REDACTED`: Mask or nullify specified PII fields while retaining allowed non-personal transaction metadata.
- `ANONYMIZE_RECORD` with state `ANONYMIZED`: Irreversibly pseudonymize or scrub identifiers so the record can no longer be linked to an individual.

#### 3. VERIFICATION Operations (Phase: `VERIFICATION`)
Used to independently confirm the final target state.
- `VERIFY_RECORD_ABSENT` with state `ABSENT`: Confirm that a prohibited record has been completely purged.
- `VERIFY_RECORD_PRESENT` with state `PRESENT`: Confirm that a policy-mandated retained record (e.g., tax/fiscal compliance) remains intact.
- `VERIFY_RECORD_REDACTED` with state `REDACTED`: Confirm that prohibited PII has been replaced with redaction masks while allowed fields remain.
- `VERIFY_RECORD_ANONYMIZED` with state `ANONYMIZED`: Confirm that irreversible pseudonymization has succeeded.
- `VERIFY_DATA_FLOW_DISABLED` with state `DISABLED`: Confirm that the replication/sync pipeline is offline or customer-excluded.
- `VERIFY_RESTORE_BLOCKED` with state `BLOCKED`: Confirm that restore barriers/filters are active.

---

### Classification Semantics

1. `NOT_APPLICABLE`:
   - Customer did not submit a deletion request (e.g., request type is `DATA_EXPORT`, `INQUIRY`, or account status is active without deletion request).
   - Expected output `steps_json`: `[]`.

2. `COMPLETE`:
   - Every applicable resource satisfies the policy rules as of `audit_at`.
   - No active data flows can recreate deleted data.
   - All backup and restore risks are resolved or blocked.
   - Required retained records (e.g., tax, order invoices subject to fiscal retention) remain available and correctly preserved.
   - Prohibited direct identifiers are purged or redacted.
   - Account tombstones retain only allowed internal system IDs and zero direct identifiers.
   - Expected output `steps_json`: Contains **VERIFICATION** steps only, each citing the valid `evidence_id` proving that condition.

3. `INCOMPLETE`:
   - One or more policy violations, remaining records, active sync flows, or restore risks exist as of `audit_at`.
   - Expected output `steps_json`:
     1. **FINDINGS** steps (citing the evidence where the issue was discovered).
     2. **REMEDIATION** steps (proposed actions; `evidence_id` is empty string `""`).
     3. **VERIFICATION** steps (future verification actions; `evidence_id` is empty string `""`).

---

### Step Execution and Output Ordering Rules

Each row in `output.csv` must adhere to:
1. Columns: `case_id`, `deletion_status`, `steps_json`.
2. Sorted in ascending order by `case_id`.
3. Strict CSV quoting: `steps_json` must be a valid JSON string array.
4. Each step object must have exactly:
   - `step_no` (integer starting at 1, increasing consecutively)
   - `phase` (`FINDINGS`, `REMEDIATION`, or `VERIFICATION`)
   - `system_id` (string)
   - `resource_id` (string)
   - `operation` (one of the 15 authoritative operations)
   - `state` (matching allowed state)
   - `evidence_id` (string reference for findings and current verification; empty string `""` for proposed remediation/verification)
5. Ordering hierarchy:
   - Phase Order: `FINDINGS` -> `REMEDIATION` -> `VERIFICATION`.
   - Within Phase:
     * Operation priority:
       * For FINDINGS: `REPORT_ACTIVE_DATA_FLOW` -> `REPORT_RESTORE_RISK` -> `REPORT_REMAINING_RECORD` -> `REPORT_EXPOSED_PII`.
       * For REMEDIATION: `DISABLE_DATA_FLOW` -> `BLOCK_RESTORE` -> `DELETE_RECORD` -> `REDACT_RECORD` -> `ANONYMIZE_RECORD`.
       * For VERIFICATION: `VERIFY_DATA_FLOW_DISABLED` -> `VERIFY_RESTORE_BLOCKED` -> `VERIFY_RECORD_ABSENT` -> `VERIFY_RECORD_PRESENT` -> `VERIFY_RECORD_REDACTED` -> `VERIFY_RECORD_ANONYMIZED`.
     * Then `system_id` ascending.
     * Then `resource_id` ascending.
