import json
import re
from typing import List, Dict, Any, Optional
from backend.engine.models import (
    DeletionRequest, CaseAuditResult, DeletionStatus,
    AuditStep, AuditPhase, AuditOperation, AuditState, EvidenceFile
)
from backend.engine.loader import DatasetLoader
from backend.engine.identity_resolver import IdentityResolver
from backend.engine.evidence_extractor import EvidenceExtractor
from backend.engine.policy_engine import PolicyEngine
from backend.engine.risk_detector import RiskDetector
from backend.engine.step_ordering import StepOrderer
from backend.engine.validator import CaseValidator

class AuditRunner:
    @staticmethod
    def _get_case_id_variants(case_id: str) -> List[str]:
        variants = [case_id.lower()]
        m = re.match(r"^case_0*(\d+)$", case_id, re.IGNORECASE)
        if m:
            num = int(m.group(1))
            padded = f"case_{num:03d}"
            unpadded = f"case_{num}"
            if padded not in variants:
                variants.append(padded)
            if unpadded not in variants:
                variants.append(unpadded)
        return variants

    def __init__(self, loader: Optional[DatasetLoader] = None):
        self.loader = loader or DatasetLoader()
        if not self.loader._is_loaded:
            self.loader.load_all()

        self.identity_resolver = IdentityResolver(
            self.loader.identities_by_customer,
            self.loader.identities_by_value
        )
        self.evidence_extractor = EvidenceExtractor(self.loader.dataset_dir)
        self.policy_engine = PolicyEngine(self.loader.rules_by_system, self.loader.rules_by_id)
        self.risk_detector = RiskDetector()
        self.validator = CaseValidator(set(self.loader.evidence_by_id.keys()))

    def audit_case(self, case_id: str) -> CaseAuditResult:
        req = self.loader.requests.get(case_id)
        if not req:
            raise ValueError(f"Case ID '{case_id}' not found in dataset")

        # 1. Non-deletion requests are NOT_APPLICABLE
        if req.request_type.upper() != "DELETION":
            steps = []
            return CaseAuditResult(
                case_id=req.case_id,
                customer_id=req.customer_id,
                requested_email=req.requested_email,
                request_type=req.request_type,
                reported_status=req.reported_status,
                deletion_status=DeletionStatus.NOT_APPLICABLE,
                steps=steps,
                steps_json=json.dumps([]),
                findings_count=0,
                remediation_count=0,
                verification_count=0,
                remediation_summary="Request type is non-deletion inquiry or export. No deletion audit required."
            )

        # 2. Resolve Master & Linked Identifiers
        resolved = self.identity_resolver.resolve_customer_identities(req)
        cid = req.customer_id
        all_ids = set([cid] + [v.lower() for v in resolved["all_identifier_values"]])

        # 3. Collect all evidence records related to this customer / case
        case_variants = self._get_case_id_variants(req.case_id)
        case_ev_list: List[EvidenceFile] = []
        for ev in self.loader.evidence_by_id.values():
            r_id = ev.resource_id.lower()
            d_lower = ev.description.lower()
            fp = ev.file_path.lower()
            matched = False

            # Match exact case_id token boundaries
            for cv in case_variants:
                pat = rf"(?<![a-zA-Z0-9]){re.escape(cv)}(?![a-zA-Z0-9])"
                if re.search(pat, fp) or re.search(pat, r_id):
                    matched = True
                    break

            if not matched and (cid.lower() in r_id or cid.lower() in d_lower or cid.lower() in fp):
                matched = True
            elif not matched:
                for ident in all_ids:
                    if len(ident) > 4 and (ident in r_id or ident in d_lower or ident in fp):
                        matched = True
                        break
            if matched:
                case_ev_list.append(ev)

        # If no evidence on record exists for this case or customer, deletion cannot be verified
        if len(case_ev_list) == 0:
            return CaseAuditResult(
                case_id=req.case_id,
                customer_id=req.customer_id,
                requested_email=req.requested_email,
                request_type=req.request_type,
                reported_status=req.reported_status,
                deletion_status=DeletionStatus.NOT_APPLICABLE,
                steps=[],
                steps_json="[]",
                findings_count=0,
                remediation_count=0,
                verification_count=0,
                resolved_identities=resolved["all_identifier_values"],
                evidence_citations=[],
                remediation_summary="No forensic evidence on record for customer in audit manifest."
            )

        # Extract evidence contents
        extracted_map = {}
        for ev in case_ev_list:
            extracted_map[ev.evidence_id] = self.evidence_extractor.extract(ev)

        # 4. Detect Active Data Flows & Restore Risks
        risks = self.risk_detector.detect_risks_in_evidence(case_ev_list, extracted_map)

        findings: List[AuditStep] = []
        remediations: List[AuditStep] = []
        verifications: List[AuditStep] = []
        current_verifications: List[AuditStep] = [] # Used if COMPLETE

        # Convert risks into findings, remediations, verifications
        for r in risks:
            if r.risk_type == "ACTIVE_DATA_FLOW":
                findings.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.FINDINGS,
                    system_id=r.system_id,
                    resource_id=r.resource_id,
                    operation=AuditOperation.REPORT_ACTIVE_DATA_FLOW,
                    state=AuditState.ACTIVE,
                    evidence_id=r.evidence_id
                ))
                remediations.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.REMEDIATION,
                    system_id=r.system_id,
                    resource_id=r.resource_id,
                    operation=AuditOperation.DISABLE_DATA_FLOW,
                    state=AuditState.DISABLED,
                    evidence_id=""
                ))
                verifications.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.VERIFICATION,
                    system_id=r.system_id,
                    resource_id=r.resource_id,
                    operation=AuditOperation.VERIFY_DATA_FLOW_DISABLED,
                    state=AuditState.DISABLED,
                    evidence_id=""
                ))
            elif r.risk_type == "RESTORE_RISK":
                findings.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.FINDINGS,
                    system_id=r.system_id,
                    resource_id=r.resource_id,
                    operation=AuditOperation.REPORT_RESTORE_RISK,
                    state=AuditState.ACTIVE,
                    evidence_id=r.evidence_id
                ))
                remediations.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.REMEDIATION,
                    system_id=r.system_id,
                    resource_id=r.resource_id,
                    operation=AuditOperation.BLOCK_RESTORE,
                    state=AuditState.BLOCKED,
                    evidence_id=""
                ))
                verifications.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.VERIFICATION,
                    system_id=r.system_id,
                    resource_id=r.resource_id,
                    operation=AuditOperation.VERIFY_RESTORE_BLOCKED,
                    state=AuditState.BLOCKED,
                    evidence_id=""
                ))

        # 5. Evaluate Data Deletion & Policy Rules on remaining evidence
        for ev in case_ev_list:
            # Skip pure risk evidence already processed
            if any(r.evidence_id == ev.evidence_id for r in risks):
                continue

            extracted = extracted_map[ev.evidence_id]
            data = extracted.parsed_data
            raw_text = extracted.raw_content
            system_id = ev.system_id
            resource_id = ev.resource_id

            # Parse state of resource from evidence content
            if system_id == "sys-auth-01":
                # Check tombstone vs active user record
                if isinstance(data, dict):
                    email_val = data.get("email")
                    phone_val = data.get("phone")
                    is_tombstone = (data.get("status") in ["TOMBSTONE", "DELETED"] or data.get("is_deleted") is True)
                    
                    # If direct PII exposed in tombstone
                    if is_tombstone:
                        has_exposed_pii = False
                        if email_val and str(email_val).upper() not in ["[REDACTED]", "REDACTED", "NULL", "NONE"]:
                            has_exposed_pii = True
                        if phone_val and str(phone_val).upper() not in ["[REDACTED]", "REDACTED", "NULL", "NONE"]:
                            has_exposed_pii = True
                        
                        if has_exposed_pii:
                            findings.append(AuditStep(
                                step_no=0,
                                phase=AuditPhase.FINDINGS,
                                system_id=system_id,
                                resource_id=resource_id,
                                operation=AuditOperation.REPORT_EXPOSED_PII,
                                state=AuditState.PRESENT,
                                evidence_id=ev.evidence_id
                            ))
                            remediations.append(AuditStep(
                                step_no=0,
                                phase=AuditPhase.REMEDIATION,
                                system_id=system_id,
                                resource_id=resource_id,
                                operation=AuditOperation.REDACT_RECORD,
                                state=AuditState.REDACTED,
                                evidence_id=""
                            ))
                            verifications.append(AuditStep(
                                step_no=0,
                                phase=AuditPhase.VERIFICATION,
                                system_id=system_id,
                                resource_id=resource_id,
                                operation=AuditOperation.VERIFY_RECORD_REDACTED,
                                state=AuditState.REDACTED,
                                evidence_id=""
                            ))
                        else:
                            # Tombstone properly redacted
                            current_verifications.append(AuditStep(
                                step_no=0,
                                phase=AuditPhase.VERIFICATION,
                                system_id=system_id,
                                resource_id=resource_id,
                                operation=AuditOperation.VERIFY_RECORD_REDACTED,
                                state=AuditState.REDACTED,
                                evidence_id=ev.evidence_id
                            ))
                    else:
                        # User record still active
                        findings.append(AuditStep(
                            step_no=0,
                            phase=AuditPhase.FINDINGS,
                            system_id=system_id,
                            resource_id=resource_id,
                            operation=AuditOperation.REPORT_REMAINING_RECORD,
                            state=AuditState.PRESENT,
                            evidence_id=ev.evidence_id
                        ))
                        remediations.append(AuditStep(
                            step_no=0,
                            phase=AuditPhase.REMEDIATION,
                            system_id=system_id,
                            resource_id=resource_id,
                            operation=AuditOperation.DELETE_RECORD,
                            state=AuditState.ABSENT,
                            evidence_id=""
                        ))
                        verifications.append(AuditStep(
                            step_no=0,
                            phase=AuditPhase.VERIFICATION,
                            system_id=system_id,
                            resource_id=resource_id,
                            operation=AuditOperation.VERIFY_RECORD_ABSENT,
                            state=AuditState.ABSENT,
                            evidence_id=""
                        ))

            elif system_id == "sys-search-es":
                # Check hits in Elasticsearch
                is_present = False
                if isinstance(data, dict):
                    hits = data.get("hits", {})
                    total_val = hits.get("total", {}).get("value", 0) if isinstance(hits.get("total"), dict) else hits.get("total", 0)
                    if total_val > 0 or len(hits.get("hits", [])) > 0:
                        is_present = True

                if is_present:
                    findings.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.FINDINGS,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.REPORT_REMAINING_RECORD,
                        state=AuditState.PRESENT,
                        evidence_id=ev.evidence_id
                    ))
                    remediations.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.REMEDIATION,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.DELETE_RECORD,
                        state=AuditState.ABSENT,
                        evidence_id=""
                    ))
                    verifications.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.VERIFICATION,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.VERIFY_RECORD_ABSENT,
                        state=AuditState.ABSENT,
                        evidence_id=""
                    ))
                else:
                    current_verifications.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.VERIFICATION,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.VERIFY_RECORD_ABSENT,
                        state=AuditState.ABSENT,
                        evidence_id=ev.evidence_id
                    ))

            elif system_id == "sys-crm-01":
                # Check if CRM contact is present or log confirms purge
                is_purged = ("crm purge success" in raw_text.lower() or "404 not found" in raw_text.lower())
                if is_purged:
                    current_verifications.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.VERIFICATION,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.VERIFY_RECORD_ABSENT,
                        state=AuditState.ABSENT,
                        evidence_id=ev.evidence_id
                    ))
                else:
                    findings.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.FINDINGS,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.REPORT_REMAINING_RECORD,
                        state=AuditState.PRESENT,
                        evidence_id=ev.evidence_id
                    ))
                    remediations.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.REMEDIATION,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.DELETE_RECORD,
                        state=AuditState.ABSENT,
                        evidence_id=""
                    ))
                    verifications.append(AuditStep(
                        step_no=0,
                        phase=AuditPhase.VERIFICATION,
                        system_id=system_id,
                        resource_id=resource_id,
                        operation=AuditOperation.VERIFY_RECORD_ABSENT,
                        state=AuditState.ABSENT,
                        evidence_id=""
                    ))

            elif system_id == "sys-orders-db":
                # Retained fiscal order record
                current_verifications.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.VERIFICATION,
                    system_id=system_id,
                    resource_id=resource_id,
                    operation=AuditOperation.VERIFY_RECORD_PRESENT,
                    state=AuditState.PRESENT,
                    evidence_id=ev.evidence_id
                ))

            elif system_id == "sys-marketing-mail":
                # Marketing mail subscription lingering
                findings.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.FINDINGS,
                    system_id=system_id,
                    resource_id=resource_id,
                    operation=AuditOperation.REPORT_REMAINING_RECORD,
                    state=AuditState.PRESENT,
                    evidence_id=ev.evidence_id
                ))
                remediations.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.REMEDIATION,
                    system_id=system_id,
                    resource_id=resource_id,
                    operation=AuditOperation.DELETE_RECORD,
                    state=AuditState.ABSENT,
                    evidence_id=""
                ))
                verifications.append(AuditStep(
                    step_no=0,
                    phase=AuditPhase.VERIFICATION,
                    system_id=system_id,
                    resource_id=resource_id,
                    operation=AuditOperation.VERIFY_RECORD_ABSENT,
                    state=AuditState.ABSENT,
                    evidence_id=""
                ))

        # 6. Final Decision & Ordered Steps Construction
        if len(findings) > 0:
            status = DeletionStatus.INCOMPLETE
            raw_steps = findings + remediations + verifications
            ordered_steps = StepOrderer.order_steps(raw_steps)
            summary = f"Audit identified {len(findings)} unresolved policy violations or active risks. Remediation required."
        elif len(current_verifications) > 0:
            status = DeletionStatus.COMPLETE
            ordered_steps = StepOrderer.order_steps(current_verifications)
            summary = f"All {len(current_verifications)} system resources verified compliant with deletion policy as of audit cutoff."
        else:
            status = DeletionStatus.NOT_APPLICABLE
            ordered_steps = []
            summary = "No verifiable compliant resources found for customer. Status classified as NOT_APPLICABLE."

        # Validate steps with CaseValidator
        issues = self.validator.validate_case(req.case_id, status.value, ordered_steps)
        if issues:
            raise ValueError(f"Validation failed for case {req.case_id}: {[str(i) for i in issues]}")

        # Serialized JSON steps
        steps_dict = [s.model_dump() for s in ordered_steps]
        steps_json = json.dumps(steps_dict)

        evidence_citations = [s.evidence_id for s in ordered_steps if s.evidence_id]

        return CaseAuditResult(
            case_id=req.case_id,
            customer_id=req.customer_id,
            requested_email=req.requested_email,
            request_type=req.request_type,
            reported_status=req.reported_status,
            deletion_status=status,
            steps=ordered_steps,
            steps_json=steps_json,
            findings_count=len(findings),
            remediation_count=len(remediations),
            verification_count=len(verifications) if status == DeletionStatus.INCOMPLETE else len(current_verifications),
            resolved_identities=resolved["all_identifier_values"],
            evidence_citations=evidence_citations,
            remediation_summary=summary
        )

    def audit_all(self) -> Dict[str, CaseAuditResult]:
        results = {}
        for case_id in sorted(self.loader.requests.keys()):
            results[case_id] = self.audit_case(case_id)
        return results
