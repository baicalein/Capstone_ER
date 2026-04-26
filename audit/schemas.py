from typing import TypedDict, Optional, Dict, Any


class AuditSchema(TypedDict):
    event_id: str
    run_id: str
    parent_event_id: Optional[str]

    node: str
    status: str  # "started" | "completed" | "error"

    start_ts: float
    end_ts: Optional[float]
    latency_ms: Optional[float]

    input: Optional[Dict[str, Any]]
    output: Optional[Dict[str, Any]]
    error: Optional[str]
