from typing import TypedDict, Optional, List, Dict, Any


class ERState(TypedDict, total=False):

    # ----------------------------
    # Input / intent
    # ----------------------------

    user_input: str
    patient_id: Optional[str]
    use_case: Optional[str]

    # ----------------------------
    # Requirement planning
    # ----------------------------

    required_resources: List[str]

    # ----------------------------
    # Validation layer output
    # ----------------------------

    validated_queries: List[Dict[str, Any]]

    # ----------------------------
    # MCP raw query results
    # ----------------------------

    patient: Optional[Dict[str, Any]]

    encounters: List[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]

    # ----------------------------
    # ER-filtered resources
    # ----------------------------

    er_encounters: List[Dict[str, Any]]
    er_encounter_ids: List[str]

    er_observations: List[Dict[str, Any]]
    er_medications: List[Dict[str, Any]]
    er_allergies: List[Dict[str, Any]]

    # ----------------------------
    # Aggregated clinical snapshot
    # ----------------------------

    aggregated_data: Optional[Dict[str, Any]]

    # ----------------------------
    # Snapshot generator output
    # ----------------------------

    snapshot: Optional[str]

    # ----------------------------
    # Observability
    # ----------------------------

    run_id: Optional[str]
    trace: Optional[List[Dict[str, Any]]]

    # ----------------------------
    # Error / validation
    # ----------------------------

    error: Optional[str]