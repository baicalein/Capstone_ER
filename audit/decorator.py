import time
import inspect
import uuid

from agent_system.utils.debug_trace import debug_trace
from audit.audit_logger import log_event


def audited_node(func):
    """
    Decorator supporting BOTH sync and async LangGraph nodes.
    Adds audit timing, error handling, and debug traces.
    """

    if inspect.iscoroutinefunction(func):

        async def async_wrapper(state, *args, **kwargs):

            node_name = func.__name__
            run_id = kwargs.get("run_id") or str(uuid.uuid4())

            start_time = time.time()
            start_event_id = str(uuid.uuid4())

            debug_trace(f"{node_name} (audit_start)", state)

            # START EVENT
            log_event({
                "event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": "started",
                "start_ts": start_time,
                "input": state
            })

            try:
                result = await func(state, *args, **kwargs)
                status = "completed"
                error = None

            except Exception as e:
                result = None
                status = "error"
                error = str(e)

            end_time = time.time()
            latency_ms = round((end_time - start_time) * 1000, 2)

            debug_trace(
                f"{node_name} (audit_end)",
                {"status": status, "latency_ms": latency_ms}
            )

            # END EVENT (success OR failure)
            log_event({
                "event_id": str(uuid.uuid4()),
                "parent_event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": status,
                "start_ts": start_time,
                "end_ts": end_time,
                "latency_ms": latency_ms,
                "output": result,
                "error": error
            })

            # Re-raise error so system behavior doesn't change
            if status == "error":
                raise

            return result

        return async_wrapper

    else:

        def sync_wrapper(state, *args, **kwargs):

            node_name = func.__name__
            run_id = kwargs.get("run_id") or str(uuid.uuid4())

            start_time = time.time()
            start_event_id = str(uuid.uuid4())

            debug_trace(f"{node_name} (audit_start)", state)

            # START EVENT
            log_event({
                "event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": "started",
                "start_ts": start_time,
                "input": state
            })

            try:
                result = func(state, *args, **kwargs)
                status = "completed"
                error = None

            except Exception as e:
                result = None
                status = "error"
                error = str(e)

            end_time = time.time()
            latency_ms = round((end_time - start_time) * 1000, 2)

            debug_trace(
                f"{node_name} (audit_end)",
                {"status": status, "latency_ms": latency_ms}
            )

            # END EVENT
            log_event({
                "event_id": str(uuid.uuid4()),
                "parent_event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": status,
                "start_ts": start_time,
                "end_ts": end_time,
                "latency_ms": latency_ms,
                "output": result,
                "error": error
            })

            if status == "error":
                raise

            return result

        return sync_wrapper
