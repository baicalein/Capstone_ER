from langgraph.types import RetryPolicy

from agent_system.error_handling.error_types import (
    MCPTimeoutError,
    MCPRateLimitError,
    MCPTransientError,
)


# --------------------------------------------------
# Retry policy for MCP executor
# --------------------------------------------------

retry_policy = RetryPolicy(
    max_attempts=3,
    backoff_factor=1.5,
    retry_on=(
        MCPTimeoutError,
        MCPRateLimitError,
        MCPTransientError,
    ),
)