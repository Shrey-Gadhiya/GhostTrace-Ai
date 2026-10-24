from typing import List, Dict, Any, Optional
from backend.engine.models import EvidenceFile

class DetectedRisk:
    def __init__(self, risk_type: str, system_id: str, resource_id: str, evidence_id: str, description: str):
        self.risk_type = risk_type # "ACTIVE_DATA_FLOW" or "RESTORE_RISK"
        self.system_id = system_id
        self.resource_id = resource_id
        self.evidence_id = evidence_id
        self.description = description

class RiskDetector:
    def detect_risks_in_evidence(self, evidence_list: List[EvidenceFile], extracted_map: Dict[str, Any]) -> List[DetectedRisk]:
        risks: List[DetectedRisk] = []
        for ev in evidence_list:
            system_id = ev.system_id
            extracted = extracted_map.get(ev.evidence_id)
            if not extracted:
                continue

            raw_lower = extracted.raw_content.lower()

            # 1. Detect Active Sync / ETL / Replication Flows
            if system_id == "sys-sync-worker" or "sync" in ev.resource_id.lower() or "pipeline" in ev.resource_id.lower():
                if "active_job" in raw_lower or "status=running" in raw_lower or "interval=" in raw_lower:
                    risks.append(DetectedRisk(
                        risk_type="ACTIVE_DATA_FLOW",
                        system_id=ev.system_id,
                        resource_id=ev.resource_id,
                        evidence_id=ev.evidence_id,
                        description=ev.description or "Active synchronization flow capable of resurrecting data"
                    ))

            # 2. Detect Restore / Backup Hazards
            if system_id == "sys-backup-s3" or "backup" in ev.resource_id.lower() or "snapshot" in ev.resource_id.lower():
                if "unblocked_restore_risk" in raw_lower or "unfiltered" in raw_lower or ("restore_filter_applied" in raw_lower and "false" in raw_lower):
                    risks.append(DetectedRisk(
                        risk_type="RESTORE_RISK",
                        system_id=ev.system_id,
                        resource_id=ev.resource_id,
                        evidence_id=ev.evidence_id,
                        description=ev.description or "Point-in-time restore risk without customer exclusion filter"
                    ))

        return risks
