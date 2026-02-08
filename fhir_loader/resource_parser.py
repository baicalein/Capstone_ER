from typing import Dict, Optional


def extract_ref_id(ref: Optional[str]) -> Optional[str]:
    """
    Convert 'ResourceType/id' -> 'id'
    """
    if not ref or "/" not in ref:
        return None
    return ref.split("/", 1)[1]


def parse_resource(obj: Dict) -> Dict:
    """
    Extract minimal, encounter-centric fields from a FHIR resource.
    """
    resource_type = obj.get("resourceType")
    resource_id = obj.get("id")

    subject_ref = obj.get("subject", {}).get("reference")
    encounter_ref = obj.get("encounter", {}).get("reference")

    return {
        "resourceType": resource_type,
        "id": resource_id,
        "patient_id": extract_ref_id(subject_ref),
        "encounter_id": extract_ref_id(encounter_ref),
    }

