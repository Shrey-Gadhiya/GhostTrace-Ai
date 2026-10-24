import csv
from pathlib import Path
from typing import Dict, List, Optional
from backend.config import settings
from backend.engine.models import (
    DeletionRequest, UserIdentity, AuditLogEntry, DeletionRule, EvidenceFile
)

class DatasetLoader:
    def __init__(self, dataset_dir: Optional[Path] = None):
        self.dataset_dir = dataset_dir or settings.DATASET_DIR
        self.requests: Dict[str, DeletionRequest] = {}
        self.identities_by_customer: Dict[str, List[UserIdentity]] = {}
        self.identities_by_value: Dict[str, List[UserIdentity]] = {}
        self.audit_logs_by_customer: Dict[str, List[AuditLogEntry]] = {}
        self.rules_by_system: Dict[str, List[DeletionRule]] = {}
        self.rules_by_id: Dict[str, DeletionRule] = {}
        self.evidence_by_id: Dict[str, EvidenceFile] = {}
        self.evidence_by_resource: Dict[str, List[EvidenceFile]] = {}
        self._is_loaded = False

    def load_all(self):
        self.load_requests()
        self.load_identities()
        self.load_audit_logs()
        self.load_rules()
        self.load_evidence_manifest()
        self._is_loaded = True

    def load_requests(self) -> Dict[str, DeletionRequest]:
        file_path = self.dataset_dir / "deletion_requests.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Missing deletion_requests.csv at {file_path}")
        
        self.requests = {}
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                req = DeletionRequest(
                    case_id=row["case_id"].strip(),
                    customer_id=row["customer_id"].strip(),
                    requested_email=row["requested_email"].strip(),
                    request_type=row["request_type"].strip(),
                    requested_at=row["requested_at"].strip(),
                    reported_status=row["reported_status"].strip(),
                    audit_at=row["audit_at"].strip()
                )
                self.requests[req.case_id] = req
        return self.requests

    def load_identities(self) -> Dict[str, List[UserIdentity]]:
        file_path = self.dataset_dir / "user_identities.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Missing user_identities.csv at {file_path}")

        self.identities_by_customer = {}
        self.identities_by_value = {}
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ident = UserIdentity(
                    identity_id=row["identity_id"].strip(),
                    primary_customer_id=row["primary_customer_id"].strip(),
                    identifier_type=row["identifier_type"].strip(),
                    identifier_value=row["identifier_value"].strip(),
                    status=row["status"].strip(),
                    source_system=row["source_system"].strip(),
                    linked_at=row["linked_at"].strip()
                )
                self.identities_by_customer.setdefault(ident.primary_customer_id, []).append(ident)
                self.identities_by_value.setdefault(ident.identifier_value.lower(), []).append(ident)
        return self.identities_by_customer

    def load_audit_logs(self) -> Dict[str, List[AuditLogEntry]]:
        file_path = self.dataset_dir / "user_audit_log.csv"
        self.audit_logs_by_customer = {}
        if not file_path.exists():
            return self.audit_logs_by_customer

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = AuditLogEntry(
                    log_id=row["log_id"].strip(),
                    system_id=row["system_id"].strip(),
                    resource_id=row["resource_id"].strip(),
                    event_type=row["event_type"].strip(),
                    actor=row["actor"].strip(),
                    timestamp=row["timestamp"].strip(),
                    details=row.get("details", "").strip()
                )
                # Store by resource or actor reference
                self.audit_logs_by_customer.setdefault(entry.actor, []).append(entry)
        return self.audit_logs_by_customer

    def load_rules(self) -> Dict[str, List[DeletionRule]]:
        file_path = self.dataset_dir / "deletion_rules.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Missing deletion_rules.csv at {file_path}")

        self.rules_by_system = {}
        self.rules_by_id = {}
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = DeletionRule(
                    rule_id=row["rule_id"].strip(),
                    system_id=row["system_id"].strip(),
                    data_category=row["data_category"].strip(),
                    required_treatment=row["required_treatment"].strip(),
                    retention_rationale=row["retention_rationale"].strip(),
                    prohibited_fields=row.get("prohibited_fields", "").strip(),
                    allowed_fields=row.get("allowed_fields", "").strip()
                )
                self.rules_by_id[rule.rule_id] = rule
                self.rules_by_system.setdefault(rule.system_id, []).append(rule)
        return self.rules_by_system

    def load_evidence_manifest(self) -> Dict[str, EvidenceFile]:
        file_path = self.dataset_dir / "evidence_files.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Missing evidence_files.csv at {file_path}")

        self.evidence_by_id = {}
        self.evidence_by_resource = {}
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ev = EvidenceFile(
                    evidence_id=row["evidence_id"].strip(),
                    system_id=row["system_id"].strip(),
                    resource_id=row["resource_id"].strip(),
                    file_path=row["file_path"].strip(),
                    file_type=row["file_type"].strip(),
                    collected_at=row["collected_at"].strip(),
                    hash_sha256=row["hash_sha256"].strip(),
                    description=row["description"].strip()
                )
                self.evidence_by_id[ev.evidence_id] = ev
                self.evidence_by_resource.setdefault(ev.resource_id, []).append(ev)
        return self.evidence_by_id
