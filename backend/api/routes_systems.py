from fastapi import APIRouter
from typing import Dict, Any, List
from backend.engine.loader import DatasetLoader

router = APIRouter()
loader = DatasetLoader()
loader.load_all()

@router.get("/systems")
def get_systems():
    # Build actual inventory from evidence and deletion rules
    systems_meta = {
        "sys-auth-01": {"name": "Account & Auth Service", "category": "Core Identity & Credentials", "env": "AWS us-east-1", "storage": "PostgreSQL"},
        "sys-crm-01": {"name": "HubSpot/Salesforce CRM", "category": "Sales & Leads Management", "env": "SaaS Integration", "storage": "Cloud CRM"},
        "sys-search-es": {"name": "Elasticsearch Search Cluster", "category": "Customer Search & Discovery", "env": "AWS OpenSearch", "storage": "Lucene Indices"},
        "sys-orders-db": {"name": "Orders & Billing Datastore", "category": "Fiscal Accounting & Orders", "env": "AWS RDS Aurora", "storage": "PostgreSQL"},
        "sys-marketing-mail": {"name": "Marketing Emailer", "category": "Campaigns & Newsletters", "env": "SendGrid / Mailchimp", "storage": "Mailing Segments"},
        "sys-lake-analytics": {"name": "Snowflake Analytics Lake", "category": "Behavioral Event Stream", "env": "Snowflake Data Warehouse", "storage": "Columnar Parquet"},
        "sys-sync-worker": {"name": "Distributed Sync & ETL Pipeline", "category": "Data Integration Workers", "env": "Kubernetes CronJobs", "storage": "Kafka / Redis"},
        "sys-backup-s3": {"name": "Glacier Backup Snapshot Vault", "category": "Point-in-Time Backups", "env": "AWS S3 Glacier Deep Archive", "storage": "Tarballs & WAL"}
    }

    result = []
    for sys_id, meta in systems_meta.items():
        rules = loader.rules_by_system.get(sys_id, [])
        ev_count = sum(1 for ev in loader.evidence_by_id.values() if ev.system_id == sys_id)
        
        has_active_flow = (sys_id == "sys-sync-worker")
        has_restore_risk = (sys_id == "sys-backup-s3")

        result.append({
            "system_id": sys_id,
            "name": meta["name"],
            "category": meta["category"],
            "environment": meta["env"],
            "storage_type": meta["storage"],
            "evidence_count": ev_count,
            "has_active_data_flow": has_active_flow,
            "has_restore_risk": has_restore_risk,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "data_category": r.data_category,
                    "required_treatment": r.required_treatment,
                    "retention_rationale": r.retention_rationale,
                    "prohibited_fields": r.prohibited_fields,
                    "allowed_fields": r.allowed_fields
                }
                for r in rules
            ]
        })

    return {"systems": result}
