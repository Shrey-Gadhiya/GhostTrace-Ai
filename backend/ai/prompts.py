"""
Version-controlled prompts for GhostTrace AI evidence interpretation and summary generation.
"""

AMBIGUOUS_EVIDENCE_PROMPT = """
You are GhostTrace AI, a senior privacy compliance auditor for Northstar Shop.
Analyze the following forensic evidence collected for customer deletion request {case_id} ({customer_id}).

EVIDENCE METADATA:
System ID: {system_id}
Resource ID: {resource_id}
File Type: {file_type}
Description: {description}

RAW EVIDENCE CONTENT:
```
{raw_content}
```

APPLICABLE DELETION POLICY:
Required Treatment: {required_treatment}
Prohibited Fields: {prohibited_fields}
Allowed Fields: {allowed_fields}

TASK:
Determine if this evidence demonstrates compliance, remaining records, exposed direct PII, active replication data flow, or restore risk.
Return STRICT JSON matching this schema:
{{
  "is_compliant": boolean,
  "issue_type": "NONE" | "REMAINING_RECORD" | "EXPOSED_PII" | "ACTIVE_DATA_FLOW" | "RESTORE_RISK",
  "rationale": "Concise forensic explanation",
  "exposed_fields": ["list", "of", "exposed", "prohibited", "fields"],
  "recommended_operation": "DELETE_RECORD" | "REDACT_RECORD" | "ANONYMIZE_RECORD" | "DISABLE_DATA_FLOW" | "BLOCK_RESTORE" | "VERIFY_RECORD_ABSENT" | "VERIFY_RECORD_PRESENT"
}}
"""

CASE_EXECUTIVE_SUMMARY_PROMPT = """
Generate a concise, enterprise privacy compliance audit summary for case {case_id} at Northstar Shop.

Customer ID: {customer_id}
Request Type: {request_type}
Reported Status: {reported_status}
Audited Status: {audited_status}
Findings Count: {findings_count}
Remediation Steps Count: {remediation_count}

Findings Detail:
{findings_text}

Provide a 2-3 sentence executive summary explaining the audit determination, whether ghost data was discovered, and the necessary remediation sequence.
"""
