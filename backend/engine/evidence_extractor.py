import json
import csv
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings
from backend.engine.models import EvidenceFile

class ExtractedEvidence:
    def __init__(self, evidence_id: str, system_id: str, resource_id: str, file_type: str, raw_content: str, parsed_data: Any, is_valid_hash: bool):
        self.evidence_id = evidence_id
        self.system_id = system_id
        self.resource_id = resource_id
        self.file_type = file_type
        self.raw_content = raw_content
        self.parsed_data = parsed_data
        self.is_valid_hash = is_valid_hash

class EvidenceExtractor:
    def __init__(self, dataset_dir: Optional[Path] = None):
        self.dataset_dir = dataset_dir or settings.DATASET_DIR
        self._cache: Dict[str, ExtractedEvidence] = {}

    def extract(self, ev: EvidenceFile) -> ExtractedEvidence:
        if ev.evidence_id in self._cache:
            return self._cache[ev.evidence_id]

        # Prevent path traversal
        rel_path = Path(ev.file_path)
        full_path = (self.dataset_dir / rel_path).resolve()
        
        # Security assertion: ensure path is inside dataset_dir
        if not str(full_path).startswith(str(self.dataset_dir.resolve())):
            raise ValueError(f"Path traversal detected in evidence file path: {ev.file_path}")

        raw_content = ""
        parsed_data = None
        is_valid_hash = False

        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    raw_content = f.read()

                # SHA256 integrity check
                actual_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
                is_valid_hash = (actual_hash == ev.hash_sha256)

                # Format-specific parsing
                ft = ev.file_type.upper()
                if ft == "JSON":
                    try:
                        parsed_data = json.loads(raw_content)
                    except Exception:
                        parsed_data = {"raw": raw_content, "error": "json_parse_error"}
                elif ft == "CSV":
                    lines = raw_content.splitlines()
                    reader = csv.DictReader(lines)
                    parsed_data = list(reader)
                elif ft in ["LOG", "SQL", "TEXT"]:
                    parsed_data = {"lines": raw_content.splitlines(), "total_lines": len(raw_content.splitlines())}
                else:
                    parsed_data = {"raw_length": len(raw_content)}
            except Exception as e:
                raw_content = f"Error reading file: {str(e)}"
                parsed_data = {"error": str(e)}
        else:
            raw_content = "FILE_NOT_FOUND"
            parsed_data = {"error": "file_not_found"}

        extracted = ExtractedEvidence(
            evidence_id=ev.evidence_id,
            system_id=ev.system_id,
            resource_id=ev.resource_id,
            file_type=ev.file_type,
            raw_content=raw_content,
            parsed_data=parsed_data,
            is_valid_hash=is_valid_hash
        )
        self._cache[ev.evidence_id] = extracted
        return extracted
