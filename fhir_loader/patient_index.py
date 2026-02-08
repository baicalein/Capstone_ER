from typing import Dict, List, Optional
from datetime import datetime


class PatientIndex:
    """
    Patient-centric derived index.

    Built from parsed FHIR resources.
    Does NOT read raw FHIR or files directly.

    Guarantees:
    - Each patient_id maps to 0+ encounters
    - Encounter ordering is deterministic
    """

    def __init__(self, encounter_index: Dict[str, List[dict]]):
        """
        Parameters
        ----------
        encounter_index : Dict[str, List[dict]]
            encounter_id -> list of parsed resources
        """
        self._patient_to_encounters: Dict[str, List[str]] = {}
        self._encounter_start: Dict[str, datetime] = {}

        self._build(encounter_index)

    def _build(self, encounter_index: Dict[str, List[dict]]):
        for enc_id, resources in encounter_index.items():
            if not resources:
                continue

            patient_id = resources[0].get("patient_id")
            if not patient_id:
                continue

            self._patient_to_encounters.setdefault(patient_id, []).append(enc_id)

            # capture encounter start time if present
            for r in resources:
                if r["resourceType"] == "Encounter" and r.get("start"):
                    try:
                        self._encounter_start[enc_id] = datetime.fromisoformat(
                            r["start"]
                        )
                    except Exception:
                        pass

        # sort encounters per patient by start time (latest last)
        for pid, encs in self._patient_to_encounters.items():
            encs.sort(key=lambda e: self._encounter_start.get(e, datetime.min))

    # ---------- Public API ----------

    def patient_ids(self) -> List[str]:
        return list(self._patient_to_encounters.keys())

    def encounters_for_patient(self, patient_id: str) -> List[str]:
        return self._patient_to_encounters.get(patient_id, [])

    def most_recent_encounter(self, patient_id: str) -> Optional[str]:
        encs = self._patient_to_encounters.get(patient_id)
        if not encs:
            return None
        return encs[-1]

