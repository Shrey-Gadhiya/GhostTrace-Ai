from typing import Dict, List, Optional
from backend.engine.models import DeletionRule

class PolicyEvaluation:
    def __init__(self, rule: DeletionRule, compliant: bool, violation_reason: str = "", required_treatment: str = ""):
        self.rule = rule
        self.compliant = compliant
        self.violation_reason = violation_reason
        self.required_treatment = required_treatment or rule.required_treatment

class PolicyEngine:
    def __init__(self, rules_by_system: Dict[str, List[DeletionRule]], rules_by_id: Dict[str, DeletionRule]):
        self.rules_by_system = rules_by_system
        self.rules_by_id = rules_by_id

    def get_rules_for_system(self, system_id: str) -> List[DeletionRule]:
        return self.rules_by_system.get(system_id, [])

    def evaluate_resource(self, system_id: str, resource_data: Dict[str, Any], data_category: Optional[str] = None) -> List[PolicyEvaluation]:
        """
        Evaluates a resource against rules matching the system_id and category.
        """
        evaluations = []
        rules = self.get_rules_for_system(system_id)
        if not rules:
            # Fallback to wildcard rules if present
            rules = self.rules_by_system.get("*", [])

        for rule in rules:
            if data_category and rule.data_category != data_category:
                continue

            treatment = rule.required_treatment.upper()
            prohibited = [f.strip().lower() for f in rule.prohibited_fields.split(",") if f.strip()]
            
            # Check for prohibited field presence
            exposed_prohibited = []
            for field in prohibited:
                if field in resource_data:
                    val = resource_data[field]
                    if val is not None and val != "" and str(val).upper() not in ["[REDACTED]", "REDACTED", "NULL"]:
                        exposed_prohibited.append(field)

            if treatment == "DELETE":
                # Record should not exist at all
                if resource_data.get("_is_present", True):
                    evaluations.append(PolicyEvaluation(
                        rule=rule,
                        compliant=False,
                        violation_reason=f"Record is still PRESENT in {system_id} when policy mandates DELETE",
                        required_treatment="DELETE"
                    ))
                else:
                    evaluations.append(PolicyEvaluation(rule=rule, compliant=True))

            elif treatment == "REDACT":
                # Record may exist, but prohibited fields must be redacted
                if exposed_prohibited:
                    evaluations.append(PolicyEvaluation(
                        rule=rule,
                        compliant=False,
                        violation_reason=f"Prohibited fields exposed: {', '.join(exposed_prohibited)} in {system_id}",
                        required_treatment="REDACT"
                    ))
                else:
                    evaluations.append(PolicyEvaluation(rule=rule, compliant=True))

            elif treatment == "ANONYMIZE":
                if exposed_prohibited:
                    evaluations.append(PolicyEvaluation(
                        rule=rule,
                        compliant=False,
                        violation_reason=f"Un-anonymized identifiers found: {', '.join(exposed_prohibited)} in {system_id}",
                        required_treatment="ANONYMIZE"
                    ))
                else:
                    evaluations.append(PolicyEvaluation(rule=rule, compliant=True))

            elif treatment == "RETAIN":
                # Retained record MUST be present, but prohibited fields must not be exposed
                if not resource_data.get("_is_present", True):
                    evaluations.append(PolicyEvaluation(
                        rule=rule,
                        compliant=False,
                        violation_reason=f"Mandatory retained record is ABSENT from {system_id}",
                        required_treatment="RETAIN"
                    ))
                elif exposed_prohibited:
                    evaluations.append(PolicyEvaluation(
                        rule=rule,
                        compliant=False,
                        violation_reason=f"Fiscal retained record contains exposed direct PII: {', '.join(exposed_prohibited)}",
                        required_treatment="REDACT"
                    ))
                else:
                    evaluations.append(PolicyEvaluation(rule=rule, compliant=True))

        return evaluations
