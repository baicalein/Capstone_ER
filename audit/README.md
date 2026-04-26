
## Audit

This folder contains the audit system that logs events for each node in the LangGraph-based multi-agent system.
This audit system provides structured event logs in the form of a JSONL file.
The purpose of a JSONL file is for easy processing, to diagnose failures quickly, and to identify performance issues in the LangGraph system.

### Design principles

-   **Full traceability**
-   **Error tracking**
-   **Debugging of agent system**
-   **Idempotent logging -** no duplicate events
-   **JSONL trace store -** append only file where all events are automatically logged
-   **Latency tracking (ms)**
-   **Supports sync and async nodes**

### Core Components

-   `audit_logger.py`\
    logging start point; enforces schema and prevents duplicates

-   `decorator.py`\
    Captures inputs, outputs, latency, and errors from nodes

-   `schemas.py`\
    Schema structure to ensure consistent formatting across all events

-   `trace_writer.py`\
    Saves traces to an append only JSONL file

-   `trace_store.jsonl`\
    All previous runs stored

### Example

To apply the audit system to a node in the langgraph system the format would be as follows:

``` python
from audit.decorator import audited_node

#this code is a snippet pulled directly from the aggregation.py file inside the /agent_system/agents folder
@audited_node
def aggregation_layer(state: Dict[str, Any]) -> Dict[str, Any]:
    debug_trace("aggregation_layer (input)", state)
    patient = state.get("patient")
```

All nodes that are audited will automatically be logged to the trace_store.jsonl file or the path defined by the TRACE_FILE environment variable.

### Current Limitations/Future Improvements

-   Currently if an event has an error or fails an event can have a start and no end

-   The JSONL file will eventually be large and it will be difficult to query and find errors.
    Potential fixes:

    -   create a dashboard or other tool to visualize traces

    -   save older logs to a database

-   Currently uses a Python `set()` meaning that unique IDs reset when the system is restarted.
    There is a small chance of duplicated event ids.
    Potential solutions:

    -   Redis

    -   Persistent store techniques
