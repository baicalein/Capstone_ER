from typing import TypeDict, Optional, Dict, Any


class AuditSchema(TypeDict):
    event_id: str #each event will have a unique id
    run_id: str #each run will have a unique id, multiple events can belong to the same run
    node: str #langgraph node name
    status: str #status, started, completed, or error
    start_ts: float #start timestamp
    end_ts: Optional[float] #end timestamp, can be None if the event is still in progress
    latency_ms: Optional[float] #time to execute the event in milliseconds, can be None if the event is still in progress
    input: Optional[Dict[str, Any]] #what was input
    output: Optional[Dict[str, Any]] #what was output, can be None if the event is still in progress or if there was an error
    error: Optional[str] #error message, can be None if there was no error