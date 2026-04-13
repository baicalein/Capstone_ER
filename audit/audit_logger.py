from audit.trace_writer import write_trace
import time

# In-memory idempotency (resets on restart)
_seen_event_ids = set()


def log_event(event: dict):
    """
    Logs an audit event idempotently with a standardized schema.
    """

    event_id = event.get("event_id")
    if not event_id:
        raise ValueError("Event must include 'event_id'")

    # Skip duplicates
    if event_id in _seen_event_ids:
        return

    _seen_event_ids.add(event_id)

    # Defaults
    event.setdefault("node", "unknown_node")
    event.setdefault("status", "unknown_status")
    event.setdefault("timestamp", time.time())
    event.setdefault("run_id", "default_run")

    # Ensure schema consistency
    event.setdefault("input", None)
    event.setdefault("output", None)
    event.setdefault("error", None)

    write_trace(event)