from typing import Dict, Any, List

from agent_system.utils.debug_trace import debug_trace
from audit.decorator import audited_node

# -----------------------------------------------------
# Identify ER encounters
# -----------------------------------------------------

def get_er_encounters(encounters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter encounters where location == 'Location/er'
    """

    er_encounters = []

    for enc in encounters:

        locations = enc.get("location", [])

        for loc in locations:

            ref = loc.get("location", {}).get("reference", "").lower()

            if ref == "location/er":
                er_encounters.append(enc)
                break

    return er_encounters


# -----------------------------------------------------
# Extract encounter IDs
# -----------------------------------------------------

def extract_encounter_ids(encounters: List[Dict[str, Any]]) -> List[str]:

    ids = []

    for enc in encounters:
        eid = enc.get("id")
        if eid:
            ids.append(eid)

    return ids


# -----------------------------------------------------
# Extract encounter id from reference
# -----------------------------------------------------

def extract_encounter_ref(reference: str) -> str:

    if not reference:
        return ""

    if "Encounter/" in reference:
        return reference.split("Encounter/")[-1]

    return reference


# -----------------------------------------------------
# Filter resources linked to ER encounters
# -----------------------------------------------------

def filter_by_encounter(
    resources: List[Dict[str, Any]],
    er_encounter_ids: List[str],
) -> List[Dict[str, Any]]:

    filtered = []

    for r in resources:

        encounter_ref = extract_encounter_ref(
            r.get("encounter", {}).get("reference", "")
        )

        if encounter_ref in er_encounter_ids:
            filtered.append(r)

    return filtered


# -----------------------------------------------------
# Aggregation Node
# -----------------------------------------------------
@audited_node
def aggregation_layer(state: Dict[str, Any]) -> Dict[str, Any]:

    debug_trace("aggregation_layer (input)", state)

    patient = state.get("patient")

    encounters = state.get("encounters", [])
    observations = state.get("observations", [])
    medications = state.get("medications", [])
    allergies = state.get("allergies", [])

    # --------------------------------------------------
    # Identify ER encounters
    # --------------------------------------------------

    er_encounters = get_er_encounters(encounters)

    if not er_encounters:

        result = {
            "error": "Patient has no ER encounter"
        }

        debug_trace("aggregation_layer (output)", result)

        return result

    er_encounter_ids = extract_encounter_ids(er_encounters)

    # --------------------------------------------------
    # Filter resources linked to ER encounter
    # --------------------------------------------------

    er_observations = filter_by_encounter(
        observations,
        er_encounter_ids,
    )

    er_medications = filter_by_encounter(
        medications,
        er_encounter_ids,
    )

    # AllergyIntolerance usually not encounter-linked
    # so we keep all allergies

    er_allergies = allergies

    # --------------------------------------------------
    # Aggregated object (for LLM snapshot)
    # --------------------------------------------------

    aggregated = {

        "patient": patient,

        "er_encounters": er_encounters,

        "er_observations": er_observations,

        "er_medications": er_medications,

        "allergies": er_allergies,
    }

    result = {

        "er_encounters": er_encounters,

        "er_encounter_ids": er_encounter_ids,

        "er_observations": er_observations,

        "er_medications": er_medications,

        "er_allergies": er_allergies,

        "aggregated_data": aggregated,
    }

    debug_trace("aggregation_layer (output)", result)

    return result