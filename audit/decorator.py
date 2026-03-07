import time
import inspect

from agent_system.utils.debug_trace import debug_trace


def audited_node(func):
    """
    Decorator supporting BOTH sync and async LangGraph nodes.
    Adds audit timing and debug traces.
    """

    if inspect.iscoroutinefunction(func):

        async def async_wrapper(state, *args, **kwargs):

            node_name = func.__name__

            start = time.time()

            debug_trace(f"{node_name} (audit_start)", state)

            result = await func(state, *args, **kwargs)

            duration = round(time.time() - start, 3)

            debug_trace(
                f"{node_name} (audit_end)",
                {"duration_seconds": duration}
            )

            return result

        return async_wrapper

    else:

        def sync_wrapper(state, *args, **kwargs):

            node_name = func.__name__

            start = time.time()

            debug_trace(f"{node_name} (audit_start)", state)

            result = func(state, *args, **kwargs)

            duration = round(time.time() - start, 3)

            debug_trace(
                f"{node_name} (audit_end)",
                {"duration_seconds": duration}
            )

            return result

        return sync_wrapper
