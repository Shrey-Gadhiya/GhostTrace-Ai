#!/usr/bin/env python3
"""
Northstar Shop Forensic Dataset Generator
HackerRank Orchestrate October 2026: "Ghost Data Still Exists"
Generates a realistic forensic audit dataset of 518 cases with evidence files.
"""

import os
import csv
import json
import hashlib
import random
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
EVIDENCE_DIR = DATASET_DIR / "evidence"

random.seed(42)

def ensure_dirs():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "json").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "logs").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "sql").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "csv").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "pdf").mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "images").mkdir(parents=True, exist_ok=True)

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def create_evidence_file(rel_path: str, content: str) -> str:
    full_path = DATASET_DIR / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def generate_dataset():
    ensure_dirs()
    print("Generating Northstar Shop forensic dataset...")

    # 1. Deletion Rules
    deletion_rules = [
        {
            "rule_id": "RULE_AUTH_PURGE",
            "system_id": "sys-auth-01",
            "data_category": "AUTHENTICATION_CREDENTIALS",
            "required_treatment": "DELETE",
            "retention_rationale": "GDPR Art. 17 - Mandatory erasure of auth credentials and passwords",
            "prohibited_fields": "password_hash,salt,auth_token,api_key",
            "allowed_fields": ""
        },
        {
            "rule_id": "RULE_AUTH_TOMBSTONE",
            "system_id": "sys-auth-01",
            "data_category": "ACCOUNT_TOMBSTONE",
            "required_treatment": "REDACT",
            "retention_rationale": "Internal ID reference integrity preservation; direct PII prohibited",
            "prohibited_fields": "email,phone,full_name,display_name",
            "allowed_fields": "customer_id,status,created_at,deleted_at"
        },
        {
            "rule_id": "RULE_CRM_PURGE",
            "system_id": "sys-crm-01",
            "data_category": "CRM_CONTACT",
            "required_treatment": "DELETE",
            "retention_rationale": "Customer contact records must be erased upon right-to-be-forgotten request",
            "prohibited_fields": "email,phone,full_name,shipping_address,notes",
            "allowed_fields": ""
        },
        {
            "rule_id": "RULE_SEARCH_PURGE",
            "system_id": "sys-search-es",
            "data_category": "SEARCH_INDEX",
            "required_treatment": "DELETE",
            "retention_rationale": "Search index documents must be de-indexed to prevent user discovery",
            "prohibited_fields": "email,full_name,username,phone,profile_bio",
            "allowed_fields": ""
        },
        {
            "rule_id": "RULE_ORDER_FISCAL",
            "system_id": "sys-orders-db",
            "data_category": "ORDER_TRANSACTION",
            "required_treatment": "RETAIN",
            "retention_rationale": "Statutory 7-year fiscal and tax accounting retention; PII masked",
            "prohibited_fields": "billing_email,customer_phone,shipping_name",
            "allowed_fields": "order_id,customer_id,total_amount,currency,order_date,tax_amount,line_items"
        },
        {
            "rule_id": "RULE_MARKETING_PURGE",
            "system_id": "sys-marketing-mail",
            "data_category": "MARKETING_PREFERENCES",
            "required_treatment": "DELETE",
            "retention_rationale": "Erasure from all newsletter and marketing outbound campaign lists",
            "prohibited_fields": "email,first_name,last_name,campaign_tags",
            "allowed_fields": ""
        },
        {
            "rule_id": "RULE_ANALYTICS_ANON",
            "system_id": "sys-lake-analytics",
            "data_category": "ANALYTICS_EVENT",
            "required_treatment": "ANONYMIZE",
            "retention_rationale": "Behavioral analytics permissible only with irreversible pseudonymization",
            "prohibited_fields": "ip_address,user_id,email,device_id",
            "allowed_fields": "session_duration,page_path,event_timestamp,anonymized_cohort"
        },
        {
            "rule_id": "RULE_BACKUP_PURGE",
            "system_id": "sys-backup-s3",
            "data_category": "BACKUP_SNAPSHOT",
            "required_treatment": "DELETE",
            "retention_rationale": "Backup snapshots must apply customer exclusion filters on restore",
            "prohibited_fields": "email,phone,full_name",
            "allowed_fields": ""
        }
    ]

    rules_path = DATASET_DIR / "deletion_rules.csv"
    with open(rules_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rule_id", "system_id", "data_category", "required_treatment",
            "retention_rationale", "prohibited_fields", "allowed_fields"
        ])
        writer.writeheader()
        writer.writerows(deletion_rules)

    # Scenarios distribution across 518 cases:
    # 001 - 020: Designated benchmark sample cases
    # 021 - 518: Scaled corpus spanning distinct compliance patterns
    
    cases = []
    identities = []
    audit_logs = []
    evidence_manifest = []
    sample_outputs = []
    output_template = []

    first_names = ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George", "Hannah", "Ian", "Julia",
                   "Kevin", "Laura", "Marcus", "Nadia", "Oliver", "Paula", "Quinn", "Rachel", "Sam", "Tara",
                   "Uma", "Victor", "Wendy", "Xavier", "Yasmine", "Zachary", "Liam", "Emma", "Noah", "Olivia"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]

    # Defined archetype scenarios for the 20 benchmark sample cases:
    archetypes = {
        1: ("COMPLETE", "standard_complete"),
        2: ("INCOMPLETE", "lingering_search_index"),
        3: ("INCOMPLETE", "active_crm_sync"),
        4: ("NOT_APPLICABLE", "data_export_request"),
        5: ("INCOMPLETE", "unredacted_tombstone"),
        6: ("COMPLETE", "retained_fiscal_order"),
        7: ("INCOMPLETE", "unblocked_backup_restore"),
        8: ("INCOMPLETE", "historical_alias_in_crm"),
        9: ("NOT_APPLICABLE", "account_inquiry"),
        10: ("INCOMPLETE", "multiple_violations_crm_and_es"),
        11: ("COMPLETE", "anonymized_analytics_and_tombstone"),
        12: ("INCOMPLETE", "late_deletion_after_audit_cutoff"),
        13: ("INCOMPLETE", "active_etl_data_flow"),
        14: ("COMPLETE", "multi_identity_fully_purged"),
        15: ("INCOMPLETE", "marketing_mail_lingering"),
        16: ("NOT_APPLICABLE", "password_reset"),
        17: ("INCOMPLETE", "exposed_pii_in_log"),
        18: ("COMPLETE", "standard_complete_with_fiscal_retain"),
        19: ("INCOMPLETE", "backup_risk_and_lingering_search"),
        20: ("COMPLETE", "complex_multi_system_verified")
    }

    base_date = datetime.datetime(2026, 10, 1, 9, 0, 0)

    for i in range(1, 519):
        case_id = f"case_{i:03d}"
        cust_id = f"CUST-2026-{1000 + i}"
        fn = first_names[(i - 1) % len(first_names)]
        ln = last_names[((i - 1) * 7) % len(last_names)]
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        old_email = f"{fn.lower()}_old_{i}@legacymail.net"

        req_time = base_date + datetime.timedelta(days=(i % 15), hours=(i % 12), minutes=(i % 45))
        audit_time = req_time + datetime.timedelta(days=7, hours=2)

        # Determine scenario
        if i in archetypes:
            target_status, scenario = archetypes[i]
        else:
            mod = i % 10
            if mod == 0 or mod == 4:
                target_status = "NOT_APPLICABLE"
                scenario = "data_export_request" if mod == 0 else "account_inquiry"
            elif mod in [1, 6, 8]:
                target_status = "COMPLETE"
                scenario = "standard_complete" if mod == 1 else "retained_fiscal_order"
            else:
                target_status = "INCOMPLETE"
                scenarios = [
                    "lingering_search_index",
                    "active_crm_sync",
                    "unredacted_tombstone",
                    "unblocked_backup_restore",
                    "historical_alias_in_crm"
                ]
                scenario = scenarios[i % len(scenarios)]

        req_type = "DELETION"
        if target_status == "NOT_APPLICABLE":
            req_type = "DATA_EXPORT" if "export" in scenario else "ACCOUNT_INQUIRY"
            reported_status = "COMPLETE"
        else:
            # Northstar Shop system erroneously reports COMPLETE even when ghost data lingers
            reported_status = "COMPLETE" if (i % 3 != 0) else "IN_PROGRESS"

        cases.append({
            "case_id": case_id,
            "customer_id": cust_id,
            "requested_email": email,
            "request_type": req_type,
            "requested_at": req_time.isoformat() + "Z",
            "reported_status": reported_status,
            "audit_at": audit_time.isoformat() + "Z"
        })

        output_template.append({
            "case_id": case_id,
            "deletion_status": "",
            "steps_json": ""
        })

        # Register User Identities
        identities.append({
            "identity_id": f"ID-{cust_id}-1",
            "primary_customer_id": cust_id,
            "identifier_type": "EMAIL",
            "identifier_value": email,
            "status": "ACTIVE",
            "source_system": "sys-auth-01",
            "linked_at": (req_time - datetime.timedelta(days=120)).isoformat() + "Z"
        })
        identities.append({
            "identity_id": f"ID-{cust_id}-2",
            "primary_customer_id": cust_id,
            "identifier_type": "INTERNAL_ID",
            "identifier_value": cust_id,
            "status": "ACTIVE",
            "source_system": "sys-auth-01",
            "linked_at": (req_time - datetime.timedelta(days=120)).isoformat() + "Z"
        })

        if scenario == "historical_alias_in_crm" or (i % 7 == 0):
            identities.append({
                "identity_id": f"ID-{cust_id}-3",
                "primary_customer_id": cust_id,
                "identifier_type": "EMAIL",
                "identifier_value": old_email,
                "status": "HISTORICAL_ALIAS",
                "source_system": "sys-crm-01",
                "linked_at": (req_time - datetime.timedelta(days=400)).isoformat() + "Z"
            })

        # Build evidence and audit steps for this case
        case_steps = []
        ev_counter = 1

        if target_status == "NOT_APPLICABLE":
            # steps_json is empty array
            if i <= 20:
                sample_outputs.append({
                    "case_id": case_id,
                    "deletion_status": "NOT_APPLICABLE",
                    "steps_json": json.dumps([])
                })
            continue

        elif target_status == "COMPLETE":
            # Scenario: COMPLETE -> Verification steps only with valid evidence citations
            # 1. sys-auth-01 tombstone verified redacted
            ev_id_auth = f"EV-AUTH-{i:03d}"
            ev_path_auth = f"evidence/json/auth_{case_id}.json"
            ev_content_auth = json.dumps({
                "customer_id": cust_id,
                "status": "TOMBSTONE",
                "email": "[REDACTED]",
                "phone": None,
                "full_name": None,
                "password_hash": None,
                "deleted_at": (req_time + datetime.timedelta(days=1)).isoformat() + "Z"
            }, indent=2)
            h_auth = create_evidence_file(ev_path_auth, ev_content_auth)
            evidence_manifest.append({
                "evidence_id": ev_id_auth,
                "system_id": "sys-auth-01",
                "resource_id": f"user_rec_{cust_id}",
                "file_path": ev_path_auth,
                "file_type": "JSON",
                "collected_at": audit_time.isoformat() + "Z",
                "hash_sha256": h_auth,
                "description": f"Verified tombstone with direct PII purged for {cust_id}"
            })

            # 2. sys-crm-01 record verified absent
            ev_id_crm = f"EV-CRM-{i:03d}"
            ev_path_crm = f"evidence/logs/crm_purge_{case_id}.log"
            ev_content_crm = f"[{req_time + datetime.timedelta(days=1)}] CRM PURGE SUCCESS: Record {cust_id} removed from sys-crm-01. Status: 404 NOT FOUND."
            h_crm = create_evidence_file(ev_path_crm, ev_content_crm)
            evidence_manifest.append({
                "evidence_id": ev_id_crm,
                "system_id": "sys-crm-01",
                "resource_id": f"crm_contact_{cust_id}",
                "file_path": ev_path_crm,
                "file_type": "LOG",
                "collected_at": audit_time.isoformat() + "Z",
                "hash_sha256": h_crm,
                "description": f"CRM contact record absent confirmation log for {cust_id}"
            })

            # 3. sys-search-es verified absent
            ev_id_es = f"EV-ES-{i:03d}"
            ev_path_es = f"evidence/json/es_search_{case_id}.json"
            ev_content_es = json.dumps({"took": 3, "timed_out": False, "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}}, indent=2)
            h_es = create_evidence_file(ev_path_es, ev_content_es)
            evidence_manifest.append({
                "evidence_id": ev_id_es,
                "system_id": "sys-search-es",
                "resource_id": f"idx_customers_{cust_id}",
                "file_path": ev_path_es,
                "file_type": "JSON",
                "collected_at": audit_time.isoformat() + "Z",
                "hash_sha256": h_es,
                "description": f"Elasticsearch customer index zero hits confirmation for {cust_id}"
            })

            # 4. If scenario includes fiscal order: sys-orders-db verified present
            ev_id_ord = f"EV-ORD-{i:03d}"
            ev_path_ord = f"evidence/sql/orders_{case_id}.sql"
            ev_content_ord = f"-- SQLite table export: orders_retained\nINSERT INTO orders_retained VALUES ('ORD-99{i}', '{cust_id}', 149.50, 'USD', '2025-05-12', 'REDACTED', 'REDACTED');\n"
            h_ord = create_evidence_file(ev_path_ord, ev_content_ord)
            evidence_manifest.append({
                "evidence_id": ev_id_ord,
                "system_id": "sys-orders-db",
                "resource_id": f"order_rec_ORD-99{i}",
                "file_path": ev_path_ord,
                "file_type": "SQL",
                "collected_at": audit_time.isoformat() + "Z",
                "hash_sha256": h_ord,
                "description": f"Fiscal order retention record with masked customer PII for {cust_id}"
            })

            # Verification steps strictly ordered:
            # Priority: VERIFY_DATA_FLOW_DISABLED -> VERIFY_RESTORE_BLOCKED -> VERIFY_RECORD_ABSENT -> VERIFY_RECORD_PRESENT -> VERIFY_RECORD_REDACTED -> VERIFY_RECORD_ANONYMIZED
            # Then system_id -> resource_id
            verified_items = [
                {
                    "phase": "VERIFICATION",
                    "system_id": "sys-crm-01",
                    "resource_id": f"crm_contact_{cust_id}",
                    "operation": "VERIFY_RECORD_ABSENT",
                    "state": "ABSENT",
                    "evidence_id": ev_id_crm
                },
                {
                    "phase": "VERIFICATION",
                    "system_id": "sys-search-es",
                    "resource_id": f"idx_customers_{cust_id}",
                    "operation": "VERIFY_RECORD_ABSENT",
                    "state": "ABSENT",
                    "evidence_id": ev_id_es
                },
                {
                    "phase": "VERIFICATION",
                    "system_id": "sys-orders-db",
                    "resource_id": f"order_rec_ORD-99{i}",
                    "operation": "VERIFY_RECORD_PRESENT",
                    "state": "PRESENT",
                    "evidence_id": ev_id_ord
                },
                {
                    "phase": "VERIFICATION",
                    "system_id": "sys-auth-01",
                    "resource_id": f"user_rec_{cust_id}",
                    "operation": "VERIFY_RECORD_REDACTED",
                    "state": "REDACTED",
                    "evidence_id": ev_id_auth
                }
            ]

            # Sort verified items by operation priority, then system_id, then resource_id
            op_priority_v = {
                "VERIFY_DATA_FLOW_DISABLED": 1,
                "VERIFY_RESTORE_BLOCKED": 2,
                "VERIFY_RECORD_ABSENT": 3,
                "VERIFY_RECORD_PRESENT": 4,
                "VERIFY_RECORD_REDACTED": 5,
                "VERIFY_RECORD_ANONYMIZED": 6
            }
            verified_items.sort(key=lambda x: (op_priority_v[x["operation"]], x["system_id"], x["resource_id"]))

            for idx, item in enumerate(verified_items, start=1):
                item["step_no"] = idx
                case_steps.append(item)

            if i <= 20:
                sample_outputs.append({
                    "case_id": case_id,
                    "deletion_status": "COMPLETE",
                    "steps_json": json.dumps(case_steps)
                })

        else:
            # target_status == "INCOMPLETE"
            # 1. FINDINGS (citing evidence_id)
            # 2. REMEDIATION (evidence_id = "")
            # 3. VERIFICATION (evidence_id = "")

            findings = []
            remediations = []
            verifications = []

            if scenario == "lingering_search_index":
                ev_id_es = f"EV-ES-{i:03d}"
                ev_path_es = f"evidence/json/es_search_{case_id}.json"
                ev_content_es = json.dumps({
                    "took": 4,
                    "hits": {
                        "total": {"value": 1, "relation": "eq"},
                        "hits": [{
                            "_index": "customers_v2",
                            "_id": f"doc_{cust_id}",
                            "_source": {"customer_id": cust_id, "email": email, "name": f"{fn} {ln}"}
                        }]
                    }
                }, indent=2)
                h_es = create_evidence_file(ev_path_es, ev_content_es)
                evidence_manifest.append({
                    "evidence_id": ev_id_es,
                    "system_id": "sys-search-es",
                    "resource_id": f"idx_customers_{cust_id}",
                    "file_path": ev_path_es,
                    "file_type": "JSON",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_es,
                    "description": f"Customer document still indexed in Elasticsearch for {cust_id}"
                })

                findings.append({
                    "phase": "FINDINGS",
                    "system_id": "sys-search-es",
                    "resource_id": f"idx_customers_{cust_id}",
                    "operation": "REPORT_REMAINING_RECORD",
                    "state": "PRESENT",
                    "evidence_id": ev_id_es
                })
                remediations.append({
                    "phase": "REMEDIATION",
                    "system_id": "sys-search-es",
                    "resource_id": f"idx_customers_{cust_id}",
                    "operation": "DELETE_RECORD",
                    "state": "ABSENT",
                    "evidence_id": ""
                })
                verifications.append({
                    "phase": "VERIFICATION",
                    "system_id": "sys-search-es",
                    "resource_id": f"idx_customers_{cust_id}",
                    "operation": "VERIFY_RECORD_ABSENT",
                    "state": "ABSENT",
                    "evidence_id": ""
                })

            elif scenario == "active_crm_sync" or scenario == "active_etl_data_flow":
                ev_id_sync = f"EV-SYNC-{i:03d}"
                ev_path_sync = f"evidence/logs/sync_worker_{case_id}.log"
                ev_content_sync = f"[{audit_time - datetime.timedelta(hours=1)}] ACTIVE_JOB: pipeline_crm_to_warehouse id=job_crm_sync_{cust_id} status=RUNNING interval=15m. Last sync processed customer {cust_id}."
                h_sync = create_evidence_file(ev_path_sync, ev_content_sync)
                evidence_manifest.append({
                    "evidence_id": ev_id_sync,
                    "system_id": "sys-sync-worker",
                    "resource_id": f"pipeline_sync_{cust_id}",
                    "file_path": ev_path_sync,
                    "file_type": "LOG",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_sync,
                    "description": f"Active recurring synchronization pipeline capable of recreating data for {cust_id}"
                })

                findings.append({
                    "phase": "FINDINGS",
                    "system_id": "sys-sync-worker",
                    "resource_id": f"pipeline_sync_{cust_id}",
                    "operation": "REPORT_ACTIVE_DATA_FLOW",
                    "state": "ACTIVE",
                    "evidence_id": ev_id_sync
                })
                remediations.append({
                    "phase": "REMEDIATION",
                    "system_id": "sys-sync-worker",
                    "resource_id": f"pipeline_sync_{cust_id}",
                    "operation": "DISABLE_DATA_FLOW",
                    "state": "DISABLED",
                    "evidence_id": ""
                })
                verifications.append({
                    "phase": "VERIFICATION",
                    "system_id": "sys-sync-worker",
                    "resource_id": f"pipeline_sync_{cust_id}",
                    "operation": "VERIFY_DATA_FLOW_DISABLED",
                    "state": "DISABLED",
                    "evidence_id": ""
                })

            elif scenario == "unredacted_tombstone":
                ev_id_tomb = f"EV-AUTH-{i:03d}"
                ev_path_tomb = f"evidence/json/auth_tomb_{case_id}.json"
                ev_content_tomb = json.dumps({
                    "customer_id": cust_id,
                    "status": "DELETED",
                    "email": email, # Prohibited PII exposed!
                    "phone": f"+1-555-{i:04d}",
                    "is_deleted": True
                }, indent=2)
                h_tomb = create_evidence_file(ev_path_tomb, ev_content_tomb)
                evidence_manifest.append({
                    "evidence_id": ev_id_tomb,
                    "system_id": "sys-auth-01",
                    "resource_id": f"tombstone_{cust_id}",
                    "file_path": ev_path_tomb,
                    "file_type": "JSON",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_tomb,
                    "description": f"Authentication tombstone retains direct PII email and phone for {cust_id}"
                })

                findings.append({
                    "phase": "FINDINGS",
                    "system_id": "sys-auth-01",
                    "resource_id": f"tombstone_{cust_id}",
                    "operation": "REPORT_EXPOSED_PII",
                    "state": "PRESENT",
                    "evidence_id": ev_id_tomb
                })
                remediations.append({
                    "phase": "REMEDIATION",
                    "system_id": "sys-auth-01",
                    "resource_id": f"tombstone_{cust_id}",
                    "operation": "REDACT_RECORD",
                    "state": "REDACTED",
                    "evidence_id": ""
                })
                verifications.append({
                    "phase": "VERIFICATION",
                    "system_id": "sys-auth-01",
                    "resource_id": f"tombstone_{cust_id}",
                    "operation": "VERIFY_RECORD_REDACTED",
                    "state": "REDACTED",
                    "evidence_id": ""
                })

            elif scenario == "unblocked_backup_restore":
                ev_id_bak = f"EV-BAK-{i:03d}"
                ev_path_bak = f"evidence/json/backup_meta_{case_id}.json"
                ev_content_bak = json.dumps({
                    "snapshot_id": f"snap_prod_20261015_{cust_id}",
                    "storage_tier": "S3_GLACIER",
                    "contains_customer": cust_id,
                    "restore_filter_applied": False,
                    "status": "UNBLOCKED_RESTORE_RISK"
                }, indent=2)
                h_bak = create_evidence_file(ev_path_bak, ev_content_bak)
                evidence_manifest.append({
                    "evidence_id": ev_id_bak,
                    "system_id": "sys-backup-s3",
                    "resource_id": f"snapshot_glacier_{cust_id}",
                    "file_path": ev_path_bak,
                    "file_type": "JSON",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_bak,
                    "description": f"Unblocked Glacier backup snapshot contains customer data without exclusion filters"
                })

                findings.append({
                    "phase": "FINDINGS",
                    "system_id": "sys-backup-s3",
                    "resource_id": f"snapshot_glacier_{cust_id}",
                    "operation": "REPORT_RESTORE_RISK",
                    "state": "ACTIVE",
                    "evidence_id": ev_id_bak
                })
                remediations.append({
                    "phase": "REMEDIATION",
                    "system_id": "sys-backup-s3",
                    "resource_id": f"snapshot_glacier_{cust_id}",
                    "operation": "BLOCK_RESTORE",
                    "state": "BLOCKED",
                    "evidence_id": ""
                })
                verifications.append({
                    "phase": "VERIFICATION",
                    "system_id": "sys-backup-s3",
                    "resource_id": f"snapshot_glacier_{cust_id}",
                    "operation": "VERIFY_RESTORE_BLOCKED",
                    "state": "BLOCKED",
                    "evidence_id": ""
                })

            elif scenario == "historical_alias_in_crm":
                ev_id_crm_alias = f"EV-CRM-{i:03d}"
                ev_path_crm_alias = f"evidence/csv/crm_leads_{case_id}.csv"
                ev_content_crm_alias = f"contact_id,email,status,owner\nCRM-LEAD-{i},{old_email},ACTIVE,sales_rep_4\n"
                h_crm_alias = create_evidence_file(ev_path_crm_alias, ev_content_crm_alias)
                evidence_manifest.append({
                    "evidence_id": ev_id_crm_alias,
                    "system_id": "sys-crm-01",
                    "resource_id": f"crm_lead_{old_email}",
                    "file_path": ev_path_crm_alias,
                    "file_type": "CSV",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_crm_alias,
                    "description": f"Historical alias {old_email} still present in CRM sales leads"
                })

                findings.append({
                    "phase": "FINDINGS",
                    "system_id": "sys-crm-01",
                    "resource_id": f"crm_lead_{old_email}",
                    "operation": "REPORT_REMAINING_RECORD",
                    "state": "PRESENT",
                    "evidence_id": ev_id_crm_alias
                })
                remediations.append({
                    "phase": "REMEDIATION",
                    "system_id": "sys-crm-01",
                    "resource_id": f"crm_lead_{old_email}",
                    "operation": "DELETE_RECORD",
                    "state": "ABSENT",
                    "evidence_id": ""
                })
                verifications.append({
                    "phase": "VERIFICATION",
                    "system_id": "sys-crm-01",
                    "resource_id": f"crm_lead_{old_email}",
                    "operation": "VERIFY_RECORD_ABSENT",
                    "state": "ABSENT",
                    "evidence_id": ""
                })

            elif scenario == "multiple_violations_crm_and_es" or scenario == "backup_risk_and_lingering_search":
                # Multiple violations: e.g. search index + backup risk
                ev_id_es = f"EV-ES-{i:03d}"
                ev_path_es = f"evidence/json/es_search_{case_id}.json"
                ev_content_es = json.dumps({
                    "took": 2,
                    "hits": {"total": {"value": 1, "relation": "eq"}, "hits": [{"_id": f"doc_{cust_id}", "_source": {"email": email}}]}
                })
                h_es = create_evidence_file(ev_path_es, ev_content_es)
                evidence_manifest.append({
                    "evidence_id": ev_id_es,
                    "system_id": "sys-search-es",
                    "resource_id": f"idx_customers_{cust_id}",
                    "file_path": ev_path_es,
                    "file_type": "JSON",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_es,
                    "description": f"Elasticsearch customer index still active for {cust_id}"
                })

                ev_id_bak = f"EV-BAK-{i:03d}"
                ev_path_bak = f"evidence/json/backup_meta_{case_id}.json"
                ev_content_bak = json.dumps({"snapshot_id": f"snap_2026_{cust_id}", "status": "UNFILTERED"})
                h_bak = create_evidence_file(ev_path_bak, ev_content_bak)
                evidence_manifest.append({
                    "evidence_id": ev_id_bak,
                    "system_id": "sys-backup-s3",
                    "resource_id": f"snapshot_glacier_{cust_id}",
                    "file_path": ev_path_bak,
                    "file_type": "JSON",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_bak,
                    "description": f"Glacier backup snapshot contains customer data without exclusion filters"
                })

                findings.extend([
                    {
                        "phase": "FINDINGS",
                        "system_id": "sys-backup-s3",
                        "resource_id": f"snapshot_glacier_{cust_id}",
                        "operation": "REPORT_RESTORE_RISK",
                        "state": "ACTIVE",
                        "evidence_id": ev_id_bak
                    },
                    {
                        "phase": "FINDINGS",
                        "system_id": "sys-search-es",
                        "resource_id": f"idx_customers_{cust_id}",
                        "operation": "REPORT_REMAINING_RECORD",
                        "state": "PRESENT",
                        "evidence_id": ev_id_es
                    }
                ])
                remediations.extend([
                    {
                        "phase": "REMEDIATION",
                        "system_id": "sys-backup-s3",
                        "resource_id": f"snapshot_glacier_{cust_id}",
                        "operation": "BLOCK_RESTORE",
                        "state": "BLOCKED",
                        "evidence_id": ""
                    },
                    {
                        "phase": "REMEDIATION",
                        "system_id": "sys-search-es",
                        "resource_id": f"idx_customers_{cust_id}",
                        "operation": "DELETE_RECORD",
                        "state": "ABSENT",
                        "evidence_id": ""
                    }
                ])
                verifications.extend([
                    {
                        "phase": "VERIFICATION",
                        "system_id": "sys-backup-s3",
                        "resource_id": f"snapshot_glacier_{cust_id}",
                        "operation": "VERIFY_RESTORE_BLOCKED",
                        "state": "BLOCKED",
                        "evidence_id": ""
                    },
                    {
                        "phase": "VERIFICATION",
                        "system_id": "sys-search-es",
                        "resource_id": f"idx_customers_{cust_id}",
                        "operation": "VERIFY_RECORD_ABSENT",
                        "state": "ABSENT",
                        "evidence_id": ""
                    }
                ])

            else:
                # Default INCOMPLETE fallback (e.g. lingering marketing email)
                ev_id_mail = f"EV-MAIL-{i:03d}"
                ev_path_mail = f"evidence/csv/mail_list_{case_id}.csv"
                ev_content_mail = f"list_id,email,subscribed\nPROMO-2026,{email},true\n"
                h_mail = create_evidence_file(ev_path_mail, ev_content_mail)
                evidence_manifest.append({
                    "evidence_id": ev_id_mail,
                    "system_id": "sys-marketing-mail",
                    "resource_id": f"mail_subscription_{cust_id}",
                    "file_path": ev_path_mail,
                    "file_type": "CSV",
                    "collected_at": audit_time.isoformat() + "Z",
                    "hash_sha256": h_mail,
                    "description": f"Active marketing mail subscription not purged for {cust_id}"
                })

                findings.append({
                    "phase": "FINDINGS",
                    "system_id": "sys-marketing-mail",
                    "resource_id": f"mail_subscription_{cust_id}",
                    "operation": "REPORT_REMAINING_RECORD",
                    "state": "PRESENT",
                    "evidence_id": ev_id_mail
                })
                remediations.append({
                    "phase": "REMEDIATION",
                    "system_id": "sys-marketing-mail",
                    "resource_id": f"mail_subscription_{cust_id}",
                    "operation": "DELETE_RECORD",
                    "state": "ABSENT",
                    "evidence_id": ""
                })
                verifications.append({
                    "phase": "VERIFICATION",
                    "system_id": "sys-marketing-mail",
                    "resource_id": f"mail_subscription_{cust_id}",
                    "operation": "VERIFY_RECORD_ABSENT",
                    "state": "ABSENT",
                    "evidence_id": ""
                })

            # Strict ordering of steps:
            # 1. Findings (REPORT_ACTIVE_DATA_FLOW -> REPORT_RESTORE_RISK -> REPORT_REMAINING_RECORD -> REPORT_EXPOSED_PII)
            op_pri_f = {
                "REPORT_ACTIVE_DATA_FLOW": 1,
                "REPORT_RESTORE_RISK": 2,
                "REPORT_REMAINING_RECORD": 3,
                "REPORT_EXPOSED_PII": 4
            }
            findings.sort(key=lambda x: (op_pri_f[x["operation"]], x["system_id"], x["resource_id"]))

            # 2. Remediation (DISABLE_DATA_FLOW -> BLOCK_RESTORE -> DELETE_RECORD -> REDACT_RECORD -> ANONYMIZE_RECORD)
            op_pri_r = {
                "DISABLE_DATA_FLOW": 1,
                "BLOCK_RESTORE": 2,
                "DELETE_RECORD": 3,
                "REDACT_RECORD": 4,
                "ANONYMIZE_RECORD": 5
            }
            remediations.sort(key=lambda x: (op_pri_r[x["operation"]], x["system_id"], x["resource_id"]))

            # 3. Verification (VERIFY_DATA_FLOW_DISABLED -> VERIFY_RESTORE_BLOCKED -> VERIFY_RECORD_ABSENT -> VERIFY_RECORD_PRESENT -> VERIFY_RECORD_REDACTED -> VERIFY_RECORD_ANONYMIZED)
            op_pri_v = {
                "VERIFY_DATA_FLOW_DISABLED": 1,
                "VERIFY_RESTORE_BLOCKED": 2,
                "VERIFY_RECORD_ABSENT": 3,
                "VERIFY_RECORD_PRESENT": 4,
                "VERIFY_RECORD_REDACTED": 5,
                "VERIFY_RECORD_ANONYMIZED": 6
            }
            verifications.sort(key=lambda x: (op_pri_v[x["operation"]], x["system_id"], x["resource_id"]))

            all_steps = findings + remediations + verifications
            for idx, step in enumerate(all_steps, start=1):
                step["step_no"] = idx
                case_steps.append(step)

            if i <= 20:
                sample_outputs.append({
                    "case_id": case_id,
                    "deletion_status": "INCOMPLETE",
                    "steps_json": json.dumps(case_steps)
                })

        # Add event to audit log
        audit_logs.append({
            "log_id": f"log_{cust_id}_req",
            "system_id": "sys-auth-01",
            "resource_id": f"user_rec_{cust_id}",
            "event_type": "DELETION_REQUESTED" if req_type == "DELETION" else "EXPORT_REQUESTED",
            "actor": f"user:{cust_id}",
            "timestamp": req_time.isoformat() + "Z",
            "details": json.dumps({"case_id": case_id, "req_type": req_type, "reported_status": reported_status})
        })

    # Save deletion_requests.csv
    req_path = DATASET_DIR / "deletion_requests.csv"
    with open(req_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "case_id", "customer_id", "requested_email", "request_type",
            "requested_at", "reported_status", "audit_at"
        ])
        writer.writeheader()
        writer.writerows(cases)

    # Save user_identities.csv
    ident_path = DATASET_DIR / "user_identities.csv"
    with open(ident_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "identity_id", "primary_customer_id", "identifier_type",
            "identifier_value", "status", "source_system", "linked_at"
        ])
        writer.writeheader()
        writer.writerows(identities)

    # Save user_audit_log.csv
    log_path = DATASET_DIR / "user_audit_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "log_id", "system_id", "resource_id", "event_type",
            "actor", "timestamp", "details"
        ])
        writer.writeheader()
        writer.writerows(audit_logs)

    # Save evidence_files.csv
    ev_manifest_path = DATASET_DIR / "evidence_files.csv"
    with open(ev_manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "evidence_id", "system_id", "resource_id", "file_path",
            "file_type", "collected_at", "hash_sha256", "description"
        ])
        writer.writeheader()
        writer.writerows(evidence_manifest)

    # Save sample_output.csv (20 benchmark ground-truth cases)
    sample_path = DATASET_DIR / "sample_output.csv"
    with open(sample_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "deletion_status", "steps_json"])
        writer.writeheader()
        writer.writerows(sample_outputs)

    # Save output_template.csv (518 rows)
    tpl_path = DATASET_DIR / "output_template.csv"
    with open(tpl_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "deletion_status", "steps_json"])
        writer.writeheader()
        writer.writerows(output_template)

    print(f"Generated {len(cases)} cases in {req_path}")
    print(f"Generated {len(identities)} identities in {ident_path}")
    print(f"Generated {len(audit_logs)} audit logs in {log_path}")
    print(f"Generated {len(evidence_manifest)} evidence entries in {ev_manifest_path}")
    print(f"Generated {len(sample_outputs)} benchmark samples in {sample_path}")
    print(f"Generated {len(output_template)} rows in {tpl_path}")

if __name__ == "__main__":
    generate_dataset()
