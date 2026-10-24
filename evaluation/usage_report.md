# GhostTrace AI — Token Usage & Cost Accounting Report
## HackerRank Orchestrate October 2026: "Ghost Data Still Exists"

### 1. Executive Summary & Cost Architecture
GhostTrace AI employs a **Deterministic-First, Evidence-Grounded Audit Engine**.

- Core audit logic, policy evaluation, state reconstruction, risk detection, and step ordering run **100% offline and deterministically** without requiring third-party API keys or incurring external API fees.
- An optional LLM orchestration interface is integrated for ambiguous evidence interpretation and executive summary generation.
- Model calls, prompt tokens, completion tokens, latency, and estimated costs are tracked and persisted.

---

### 2. Operational Metrics & Accounting

| Metric | Measured Value |
|---|---|
| **Model Provider** | `mock` |
| **Model Identifier** | `gemini-1.5-flash` |
| **Total Model Invocations** | `0` |
| **Total Prompt Tokens** | `0` |
| **Total Completion Tokens** | `0` |
| **Total Combined Tokens** | `0` |
| **Average Tokens Per Case** | `0` |
| **Estimated Total Cost (USD)** | **$0.0000 USD** |
| **Pricing Baseline** | Gemini 1.5 Flash ($0.075/1M input, $0.30/1M output) |

---

### 3. Model Breakdown

*Zero external LLM calls were made in this run (100% deterministic local execution). Total cost: $0.0000 USD.*

---

### 4. Privacy & Cost Control Governance
- **No Direct Identifiers Sent to Cloud APIs:** When configured with external models, raw identifiers are masked or processed locally.
- **Strict Bounded Retries:** Retries are bounded to 1 with deterministic fallback on timeout or JSON parse errors.
- **Zero API Key Leakage:** Credentials are read exclusively from environment variables (`.env`) and never exposed to the frontend browser bundle.
