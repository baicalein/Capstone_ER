from typing import Dict, Any, List

from langgraph.types import interrupt

from agent_system.utils.debug_trace import debug_trace
from audit.decorator import audited_node


# --------------------------------------------------
# Allowed FHIR resources (dataset schema)
# --------------------------------------------------

ALLOWED_RESOURCES = [
    "Location",
    "Practitioner",
    "Patient",
    "EpisodeOfCare",
    "Encounter",
    "AllergyIntolerance",
    "Goal",
    "Immunization",
    "Procedure",
    "MedicationRequest",
    "FamilyMemberHistory",
    "Observation",
    "ImagingStudy",
    "DiagnosticReport",
    "DocumentReference",
]


# --------------------------------------------------
# Allowed search parameters
# --------------------------------------------------

ALLOWED_SEARCH_PARAMS = {

    "Patient": ["_id"],

    "Encounter": ["patient"],

    "MedicationRequest": ["patient"],

    "AllergyIntolerance": ["patient"],

    "Observation": ["patient"],

    "Procedure": ["patient"],

    "DiagnosticReport": ["patient"],

    "ImagingStudy": ["patient"],

    "DocumentReference": ["patient"],

    "FamilyMemberHistory": ["patient"],

    "EpisodeOfCare": ["patient"],

    "Goal": ["patient"],

    "Immunization": ["patient"],
}


# --------------------------------------------------
# Validation Layer
# --------------------------------------------------

@audited_node
def validation_layer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate planned FHIR queries and produce
    safe executable queries for the MCP executor.
    """

    debug_trace("validation_layer (input)", state)

    patient_id = state.get("patient_id")

    # --------------------------------------------------
    # Guardrail: require patient_id
    # --------------------------------------------------

    if not patient_id:
        interrupt("patient_id is required to query FHIR resources")

    required_resources: List[str] = state.get("required_resources", [])

    validated_queries: List[Dict[str, Any]] = []

    for resource in required_resources:

        # --------------------------------------------------
        # Resource safety check
        # --------------------------------------------------

        if resource not in ALLOWED_RESOURCES:
            continue

        # --------------------------------------------------
        # Build safe query
        # --------------------------------------------------

        if resource == "Patient":

            query = {
                "resource": "Patient",
                "params": {"_id": patient_id},
            }

        else:

            query = {
                "resource": resource,
                "params": {"patient": patient_id},
            }

        # --------------------------------------------------
        # Parameter safety check
        # --------------------------------------------------

        allowed_params = ALLOWED_SEARCH_PARAMS.get(resource, [])

        safe_params = {
            k: v for k, v in query["params"].items()
            if k in allowed_params
        }

        query["params"] = safe_params

        validated_queries.append(query)

    result = {
        "validated_queries": validated_queries
    }

    debug_trace("validation_layer (output)", result)

    return result