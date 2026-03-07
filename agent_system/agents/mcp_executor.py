import json
from typing import Dict, Any, List

from mcp_client.mcp_client import MCPClient
from agent_system.error_handling.retry_policies import retry_policy
from audit.decorator import audited_node
from agent_system.utils.debug_trace import debug_trace

from agent_system.error_handling.error_types import (
    MCPTimeoutError,
    MCPRateLimitError,
    MCPTransientError,
    MCPResponseFormatError,
)


# -----------------------------------------------------
# RESOURCE OUTPUT NORMALIZATION
# -----------------------------------------------------

RESOURCE_OUTPUT_MAP = {
    "Patient": "patient",
    "Encounter": "encounters",
    "Observation": "observations",
    "MedicationRequest": "medications",
    "AllergyIntolerance": "allergies",
}


# -----------------------------------------------------
# MCP RESPONSE UNWRAPPER
# -----------------------------------------------------

def parse_bundle(result: Any) -> Dict[str, Any]:
    """
    Convert MCP TextContent response to Python dict.
    """

    try:
        return json.loads(result.content[0].text)

    except Exception as e:
        raise MCPResponseFormatError(
            f"Invalid MCP response format: {e}"
        ) from e


# -----------------------------------------------------
# BUNDLE → RESOURCE LIST
# -----------------------------------------------------

def bundle_to_resources(payload: Any) -> List[Dict[str, Any]]:

    if payload is None:
        return []

    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]

    if isinstance(payload, dict):

        if payload.get("resourceType") == "Bundle":

            entries = payload.get("entry", [])

            return [
                entry["resource"]
                for entry in entries
                if isinstance(entry, dict)
                and isinstance(entry.get("resource"), dict)
            ]

        return [payload]

    raise MCPResponseFormatError(
        f"Unsupported MCP payload type: {type(payload)}"
    )


# -----------------------------------------------------
# SAFE MCP SEARCH
# -----------------------------------------------------

async def safe_mcp_search(
    mcp_client: MCPClient,
    resource_type: str,
    search_param: Dict[str, Any],
) -> Dict[str, Any]:

    try:

        result = await mcp_client.search(
            resource_type=resource_type,
            search_param=search_param,
        )

        return parse_bundle(result)

    except TimeoutError as e:
        raise MCPTimeoutError(str(e)) from e

    except Exception as e:

        msg = str(e).lower()

        if "rate limit" in msg or "429" in msg:
            raise MCPRateLimitError(str(e)) from e

        if any(
            x in msg
            for x in [
                "temporary",
                "temporarily",
                "connection reset",
                "502",
                "503",
            ]
        ):
            raise MCPTransientError(str(e)) from e

        raise


# -----------------------------------------------------
# MCP EXECUTOR NODE
# -----------------------------------------------------
@audited_node
async def mcp_executor(
    state: Dict[str, Any],
    mcp_client: MCPClient,
) -> Dict[str, Any]:
    """
    Execute validated FHIR queries produced by validation_layer.
    """

    debug_trace("mcp_executor (input)", state)

    queries = state.get("validated_queries", [])

    results: Dict[str, List[Dict[str, Any]]] = {}

    for query in queries:

        resource_type = query["resource"]
        params = query["params"]

        payload = await safe_mcp_search(
            mcp_client,
            resource_type,
            params,
        )

        resources = bundle_to_resources(payload)

        # -----------------------------------------------------
        # Normalize output key
        # -----------------------------------------------------

        key = RESOURCE_OUTPUT_MAP.get(resource_type, resource_type)

        results[key] = resources

    # -----------------------------------------------------
    # Convert patient list → single object
    # -----------------------------------------------------

    if "patient" in results and results["patient"]:
        results["patient"] = results["patient"][0]

    # -----------------------------------------------------
    # Helpful debug summary
    # -----------------------------------------------------

    summary = {
        k: (len(v) if isinstance(v, list) else 1)
        for k, v in results.items()
    }

    debug_trace("mcp_executor (resource_counts)", summary)

    debug_trace("mcp_executor (output)", results)

    return results