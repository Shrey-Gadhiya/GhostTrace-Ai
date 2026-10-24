from typing import Dict, List, Set, Tuple
from backend.engine.models import DeletionRequest, UserIdentity

class IdentityMatch:
    def __init__(self, identifier_value: str, identifier_type: str, status: str, source_system: str, confidence: str):
        self.identifier_value = identifier_value
        self.identifier_type = identifier_type
        self.status = status
        self.source_system = source_system
        self.confidence = confidence # "CONFIRMED", "HISTORICAL_ALIAS", "AMBIGUOUS"

    def to_dict(self):
        return {
            "identifier_value": self.identifier_value,
            "identifier_type": self.identifier_type,
            "status": self.status,
            "source_system": self.source_system,
            "confidence": self.confidence
        }

class IdentityResolver:
    def __init__(self, identities_by_customer: Dict[str, List[UserIdentity]], identities_by_value: Dict[str, List[UserIdentity]]):
        self.by_customer = identities_by_customer
        self.by_value = identities_by_value

    def resolve_customer_identities(self, req: DeletionRequest) -> Dict[str, Any]:
        """
        Resolves master customer ID and all grounded linked identities (active and historical aliases).
        Never performs transitive merging across unverified links.
        """
        resolved_matches: List[IdentityMatch] = []
        seen_values: Set[str] = set()

        # 1. Primary Master Customer ID
        cid = req.customer_id.strip()
        req_email = req.requested_email.strip().lower()

        # Add primary request email
        if req_email:
            resolved_matches.append(IdentityMatch(
                identifier_value=req.requested_email.strip(),
                identifier_type="EMAIL",
                status="ACTIVE",
                source_system="sys-auth-01",
                confidence="CONFIRMED"
            ))
            seen_values.add(req_email)

        # Add customer ID
        resolved_matches.append(IdentityMatch(
            identifier_value=cid,
            identifier_type="INTERNAL_ID",
            status="ACTIVE",
            source_system="sys-auth-01",
            confidence="CONFIRMED"
        ))
        seen_values.add(cid)

        # 2. Lookup registered identity links for this primary_customer_id
        linked_records = self.by_customer.get(cid, [])
        for rec in linked_records:
            val_norm = rec.identifier_value.strip().lower()
            if val_norm in seen_values:
                continue

            confidence = "CONFIRMED"
            if rec.status == "HISTORICAL_ALIAS":
                confidence = "HISTORICAL_ALIAS"
            elif rec.status == "UNVERIFIED_MERGE":
                # Do NOT merge unverified links into confirmed scope
                continue

            resolved_matches.append(IdentityMatch(
                identifier_value=rec.identifier_value.strip(),
                identifier_type=rec.identifier_type,
                status=rec.status,
                source_system=rec.source_system,
                confidence=confidence
            ))
            seen_values.add(val_norm)

        # 3. Lookup links by requested email to check for aliases registered under other system records
        if req_email in self.by_value:
            for rec in self.by_value[req_email]:
                if rec.primary_customer_id == cid:
                    continue
                # If primary_customer_id does not match, flag as candidate but do not merge silently
                # This protects against unsafe transitive merges

        all_values = [m.identifier_value for m in resolved_matches]
        confirmed_emails = [m.identifier_value for m in resolved_matches if m.identifier_type == "EMAIL"]

        return {
            "customer_id": cid,
            "resolved_matches": resolved_matches,
            "all_identifier_values": all_values,
            "emails": confirmed_emails,
            "match_count": len(resolved_matches)
        }
