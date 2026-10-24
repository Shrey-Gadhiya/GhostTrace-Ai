from typing import Dict, Any, List, Optional
import datetime

# Standard pricing catalog (USD per 1M tokens) as of October 2026
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gemini-1.5-flash": {"input_per_million": 0.075, "output_per_million": 0.30},
    "gemini-1.5-pro": {"input_per_million": 1.25, "output_per_million": 5.00},
    "gpt-4o-mini": {"input_per_million": 0.15, "output_per_million": 0.60},
    "mock": {"input_per_million": 0.0, "output_per_million": 0.0}
}

class LLMCallRecord:
    def __init__(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int, cost_usd: float, latency_ms: float, success: bool, purpose: str):
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.provider = provider
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens
        self.cost_usd = cost_usd
        self.latency_ms = latency_ms
        self.success = success
        self.purpose = purpose

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "purpose": self.purpose
        }

class CostTracker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CostTracker, cls).__new__(cls)
            cls._instance.records: List[LLMCallRecord] = []
        return cls._instance

    def log_call(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int, latency_ms: float = 0.0, success: bool = True, purpose: str = "audit_analysis") -> LLMCallRecord:
        pricing = MODEL_PRICING.get(model, MODEL_PRICING.get("mock", {"input_per_million": 0.0, "output_per_million": 0.0}))
        cost = (prompt_tokens / 1_000_000.0 * pricing["input_per_million"]) + (completion_tokens / 1_000_000.0 * pricing["output_per_million"])
        
        record = LLMCallRecord(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=round(cost, 6),
            latency_ms=latency_ms,
            success=success,
            purpose=purpose
        )
        self.records.append(record)
        return record

    def get_summary(self) -> Dict[str, Any]:
        total_calls = len(self.records)
        total_prompt = sum(r.prompt_tokens for r in self.records)
        total_completion = sum(r.completion_tokens for r in self.records)
        total_tokens = total_prompt + total_completion
        total_cost = sum(r.cost_usd for r in self.records)

        by_model = {}
        for r in self.records:
            bm = by_model.setdefault(r.model, {"calls": 0, "tokens": 0, "cost": 0.0})
            bm["calls"] += 1
            bm["tokens"] += r.total_tokens
            bm["cost"] += r.cost_usd

        return {
            "total_calls": total_calls,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "breakdown_by_model": by_model,
            "recent_records": [r.to_dict() for r in self.records[-10:]]
        }

    def clear(self):
        self.records = []

tracker = CostTracker()
