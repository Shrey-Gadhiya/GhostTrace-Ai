import csv
import json
from pathlib import Path
from typing import Dict, List, Optional
from backend.config import settings
from backend.engine.models import CaseAuditResult

class OutputCSVWriter:
    @staticmethod
    def write_output_csv(results: Dict[str, CaseAuditResult], output_path: Optional[Path] = None) -> Path:
        target_path = output_path or settings.OUTPUT_FILE
        target_path.parent.mkdir(parents=True, exist_ok=True)

        sorted_case_ids = sorted(results.keys())

        with open(target_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            # Authoritative header
            writer.writerow(["case_id", "deletion_status", "steps_json"])
            
            for cid in sorted_case_ids:
                res = results[cid]
                # Ensure steps_json is string
                steps_str = res.steps_json if isinstance(res.steps_json, str) else json.dumps(res.steps_json)
                status_str = res.deletion_status.value if hasattr(res.deletion_status, "value") else str(res.deletion_status)
                writer.writerow([res.case_id, status_str, steps_str])

        # Immediate round-trip validation
        OutputCSVWriter.validate_roundtrip(target_path, expected_count=len(sorted_case_ids))
        return target_path

    @staticmethod
    def validate_roundtrip(file_path: Path, expected_count: Optional[int] = None) -> int:
        if not file_path.exists():
            raise FileNotFoundError(f"Output CSV not found at {file_path}")

        row_count = 0
        last_case_id = ""

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["case_id", "deletion_status", "steps_json"]:
                raise ValueError(f"Invalid columns in {file_path}. Expected ['case_id', 'deletion_status', 'steps_json'], got {reader.fieldnames}")

            for row in reader:
                row_count += 1
                cid = row["case_id"]
                status = row["deletion_status"]
                steps_raw = row["steps_json"]

                if cid <= last_case_id:
                    raise ValueError(f"Cases not strictly sorted in ascending order: '{cid}' after '{last_case_id}'")
                last_case_id = cid

                # Parse JSON
                try:
                    steps = json.loads(steps_raw)
                    if not isinstance(steps, list):
                        raise ValueError(f"steps_json for {cid} is not a JSON array")
                except Exception as e:
                    raise ValueError(f"JSON parse error for {cid} in {file_path}: {str(e)}")

        if expected_count is not None and row_count != expected_count:
            raise ValueError(f"Expected {expected_count} rows in {file_path}, got {row_count}")

        return row_count
