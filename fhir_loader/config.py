from pathlib import Path
import os

from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

# ---- Core paths ----

FHIR_DATA_ROOT = os.getenv("FHIR_DATA_ROOT")

if not FHIR_DATA_ROOT:
    raise RuntimeError(
        "FHIR_DATA_ROOT is not set. "
        "Check your .env file."
    )

FHIR_DATA_ROOT = Path(FHIR_DATA_ROOT)

if not FHIR_DATA_ROOT.exists():
    raise RuntimeError(
        f"FHIR_DATA_ROOT does not exist: {FHIR_DATA_ROOT}"
    )

