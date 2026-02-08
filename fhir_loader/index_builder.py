from collections import defaultdict
from typing import Dict, List

from fhir_loader.file_scanner import iter_fhir_files
from fhir_loader.resource_parser import parse_resource


def build_encounter_index() -> Dict[str, List[Dict]]:
    """
    Build an encounter-centric index from local FHIR JSON files.

    Scans all FHIR files discovered by `iter_fhir_files()`, parses each
    resource using `parse_resource()`, and groups parsed resources by
    encounter ID.

    Returns
    -------
    Dict[str, List[Dict]]
        Mapping:
            encounter_id -> list of parsed resource dictionaries

        Each parsed resource dict is guaranteed to include:
            - resourceType : str
            - id           : str
            - patient_id   : Optional[str]
            - encounter_id : Optional[str]

    Notes
    -----
    - Resources without an encounter_id are intentionally excluded.
    - Files that cannot be opened or parsed are skipped safely.
    - This function is PHI-safe and intended for local-only use.
    """
    index: Dict[str, List[Dict]] = defaultdict(list)

    for path in iter_fhir_files():
        try:
            with open(path) as fh:
                import json
                obj = json.load(fh)
        except Exception:
            continue

        parsed = parse_resource(obj)
        enc_id = parsed.get("encounter_id")

        # Only index resources that are encounter-linked
        if enc_id is not None:
            index[enc_id].append(parsed)

    return index


