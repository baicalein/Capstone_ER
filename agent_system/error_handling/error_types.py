class MCPError(Exception):
    """Base MCP execution error."""


class MCPTimeoutError(MCPError):
    """Timeout from MCP or downstream FHIR server."""


class MCPRateLimitError(MCPError):
    """Rate limit from MCP or downstream service."""


class MCPTransientError(MCPError):
    """Retryable temporary MCP failure."""


class MCPResponseFormatError(MCPError):
    """Unexpected MCP response structure."""
