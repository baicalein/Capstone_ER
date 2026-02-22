from pathlib import Path
from typing import List

from fhir_loader.config import FHIR_DATA_ROOT


def iter_fhir_files() -> List[Path]:
    """
    Return all FHIR JSON files under FHIR_DATA_ROOT.
    """
    return list(FHIR_DATA_ROOT.rglob("*.json"))

