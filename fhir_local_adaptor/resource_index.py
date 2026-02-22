from typing import Dict, List, Optional


class ResourceIndex:
    """
    Read-only interface over an encounter-centric FHIR resource index.

    This class does NOT parse files or load JSON.
    It operates purely on the output of `build_encounter_index()`.
    """

    def __init__(self, encounter_index: Dict[str, List[Dict]]):
        """
        Parameters
        ----------
        encounter_index : Dict[str, List[Dict]]
            Mapping:
                encounter_id -> list of parsed FHIR resource dicts
        """
        self._index = encounter_index

    # -------------------------
    # Basic accessors
    # -------------------------

    def encounter_ids(self) -> List[str]:
        """Return all encounter IDs in the index."""
        return list(self._index.keys())

    def resources_for_encounter(self, encounter_id: str) -> List[Dict]:
        """Return all resources linked to a given encounter."""
        return self._index.get(encounter_id, [])

    # -------------------------
    # Convenience helpers
    # -------------------------

    def resource_types_for_encounter(self, encounter_id: str) -> List[str]:
        """Return resourceType values for a given encounter."""
        return [
            r.get("resourceType")
            for r in self.resources_for_encounter(encounter_id)
        ]

    def count_resources(self, resource_type: Optional[str] = None) -> int:
        """
        Count resources across all encounters.

        If resource_type is provided, only count matching resources.
        """
        count = 0
        for resources in self._index.values():
            for r in resources:
                if resource_type is None or r.get("resourceType") == resource_type:
                    count += 1
        return count


