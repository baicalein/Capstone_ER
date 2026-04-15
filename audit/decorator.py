import time
import inspect
import uuid

from agent_system.utils.debug_trace import debug_trace
from audit.audit_logger import log_event


def audited_node(func):
    """
    Decorator supporting BOTH sync and async LangGraph nodes.
    Adds audit timing and debug traces.
    """

    if inspect.iscoroutinefunction(func):

        async def async_wrapper(state, *args, **kwargs):

            node_name = func.__name__
            run_id = kwargs.get("run_id") or str(uuid.uuid4())

            start = time.time()

            debug_trace(f"{node_name} (audit_start)", state)

            # start audit
            start_event_id = str(uuid.uuid4())
            log_event({
                "event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": "started",
                "input": state
            })

            result = await func(state, *args, **kwargs)

            duration = round(time.time() - start, 3)

            debug_trace(
                f"{node_name} (audit_end)",
                {"duration_seconds": duration}
            )

            # complete audit
            log_event({
                "event_id": str(uuid.uuid4()),
                "parent_event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": "completed",
                "duration_seconds": duration,
                "output": result
            })

            return result

        return async_wrapper

    else:

        def sync_wrapper(state, *args, **kwargs):

            node_name = func.__name__
            run_id = kwargs.get("run_id") or str(uuid.uuid4())

            start = time.time()

            debug_trace(f"{node_name} (audit_start)", state)

            # start audit
            start_event_id = str(uuid.uuid4())
            log_event({
                "event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": "started",
                "input": state
            })

            result = func(state, *args, **kwargs)

            duration = round(time.time() - start, 3)

            debug_trace(
                f"{node_name} (audit_end)",
                {"duration_seconds": duration}
            )

            # complete audit
            log_event({
                "event_id": str(uuid.uuid4()),
                "parent_event_id": start_event_id,
                "run_id": run_id,
                "node": node_name,
                "status": "completed",
                "duration_seconds": duration,
                "output": result
            })

            return result

        return sync_wrapper
