"""
FHIR US Core synthetic data generator (fhir.resources-free)

- Builds FHIR resources as plain dicts
- Validates them with the HL7 FHIR validator CLI JAR
  against a local US Core package folder (e.g. package_v8.0.1_R4)

Run as:
  $  poetry run uscore-synth generate

Test run - save output to output.log:
  $ poetry run uscore-synth generate --workers 1 --mrns-per-year 10 > output.log 2>&1 

NOTE: Setup JAVA path to run validator as:
  $ set_java_path.ps1  
"""

import os
import csv
import json
import uuid
import random
import string
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from multiprocessing import Pool
from typing import List, Tuple, Optional, Dict, Any

from faker import Faker

from .config import GeneratorConfig
# from .smart_patients import generate_smart_patients

faker = Faker()

# -------------------------------------------------------------------
# Local US Core profile paths
# -------------------------------------------------------------------
def build_local_profile_paths(uscore_root: str) -> dict:
    if not os.path.isdir(uscore_root):
        raise RuntimeError(f"US Core profile directory does not exist: {uscore_root}")

    return {
        "PATIENT": os.path.join(uscore_root, "StructureDefinition-us-core-patient.json"),
        "ENCOUNTER": os.path.join(uscore_root, "StructureDefinition-us-core-encounter.json"),
        "CONDITION": os.path.join(uscore_root, "StructureDefinition-us-core-condition.json"),
        "PROCEDURE": os.path.join(uscore_root, "StructureDefinition-us-core-procedure.json"),
        "IMMUNIZATION": os.path.join(uscore_root, "StructureDefinition-us-core-immunization.json"),
        "MEDREQ": os.path.join(uscore_root, "StructureDefinition-us-core-medicationrequest.json"),
        "LAB_OBS": os.path.join(uscore_root, "StructureDefinition-us-core-observation-lab.json"),
        "VITALS": os.path.join(uscore_root, "StructureDefinition-us-core-vital-signs.json"),
        "DIAG_REPORT": os.path.join(uscore_root, "StructureDefinition-us-core-diagnosticreport-lab.json"),
        "ALLERGY": os.path.join(uscore_root, "StructureDefinition-us-core-allergyintolerance.json"),
        "DOCREF": os.path.join(uscore_root, "StructureDefinition-us-core-documentreference.json"),
    }


# -------------------------------------------------------------------
# Local US Core profile paths
# -------------------------------------------------------------------
# def build_profile_paths(uscore_root: str) -> dict:
def build_profile_paths() -> dict:
    """
    Versioned canonical URLs (|8.0.1)
    This ensures validation is pinned to the exact US Core release.
    The HL7 FHIR Validator resolves these automatically.
    """

    return {
        "PATIENT":       "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient|8.0.1",
        "ENCOUNTER":     "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter|8.0.1",
        "CONDITION":     "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition|8.0.1",
        "PROCEDURE":     "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure|8.0.1",
        "IMMUNIZATION":  "http://hl7.org/fhir/us/core/StructureDefinition/us-core-immunization|8.0.1",
        "MEDREQ":        "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest|8.0.1",
        "LAB_OBS":       "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab|8.0.1",
        "VITALS":        "http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs|8.0.1",
        "DIAG_REPORT":   "http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-lab|8.0.1",
        "ALLERGY":       "http://hl7.org/fhir/us/core/StructureDefinition/us-core-allergyintolerance|8.0.1",
        "DOCREF":        "http://hl7.org/fhir/us/core/StructureDefinition/us-core-documentreference|8.0.1",
    }


def uscore_meta(local_profile_path: str) -> Dict[str, Any]:
    # meta.profile contains local StructureDefinition file path
    return {"profile": [local_profile_path]}


# -------------------------------------------------------------------
# Clinical lists
# -------------------------------------------------------------------
SURGERIES = [
    {"code": "80146002", "desc": "Appendectomy, laparoscopic"},
    {"code": "232717009", "desc": "Laparoscopic cholecystectomy"},
    {"code": "232717008", "desc": "Coronary artery bypass graft"},
    {"code": "387713003", "desc": "Total abdominal hysterectomy"},
    {"code": "409063005", "desc": "Total knee arthroplasty"},
    {"code": "80146003", "desc": "Open appendectomy"},
    {"code": "2751000126106", "desc": "Laparoscopic inguinal hernia repair"},
    {"code": "71388002", "desc": "Hip replacement, total"},
    {"code": "80146004", "desc": "Tonsillectomy"},
    {"code": "428191000124107", "desc": "Endoscopic sinus surgery"},
    {"code": "387713004", "desc": "Partial colectomy"},
    {"code": "232717010", "desc": "Laparoscopic splenectomy"},
    {"code": "409063006", "desc": "Shoulder arthroplasty"},
    {"code": "80146005", "desc": "Carotid endarterectomy"},
    {"code": "2751000126107", "desc": "Transurethral resection of the prostate (TURP)"},
]

IMMUNIZATIONS = [
    {"vaccine": "Influenza", "cvx": "140", "loinc": "59784-9"},
    {"vaccine": "COVID-19", "cvx": "207", "loinc": "94531-1"},
    {"vaccine": "Tdap", "cvx": "115", "loinc": "59783-1"},
    {"vaccine": "MMR", "cvx": "03", "loinc": "59782-3"},
    {"vaccine": "Hepatitis B", "cvx": "08", "loinc": "59781-5"},
    {"vaccine": "Varicella", "cvx": "21", "loinc": "59780-7"},
    {"vaccine": "HPV", "cvx": "62", "loinc": "59779-5"},
    {"vaccine": "Pneumococcal Conjugate (PCV13)", "cvx": "133", "loinc": "59778-3"},
    {"vaccine": "Hepatitis A", "cvx": "42", "loinc": "59777-1"},
    {"vaccine": "Rotavirus", "cvx": "122", "loinc": "59776-9"},
]

MEDICATIONS = [
    {"name": "Lisinopril", "dose": "10 mg", "rxnorm": "8610"},
    {"name": "Metformin", "dose": "500 mg", "rxnorm": "8609"},
    {"name": "Atorvastatin", "dose": "20 mg", "rxnorm": "83367"},
    {"name": "Amoxicillin", "dose": "500 mg", "rxnorm": "723"},
    {"name": "Albuterol", "dose": "90 mcg", "rxnorm": "435"},
    {"name": "Levothyroxine", "dose": "50 mcg", "rxnorm": "29046"},
    {"name": "Omeprazole", "dose": "20 mg", "rxnorm": "190"},
    {"name": "Sertraline", "dose": "50 mg", "rxnorm": "3091"},
    {"name": "Amlodipine", "dose": "5 mg", "rxnorm": "197361"},
    {"name": "Simvastatin", "dose": "20 mg", "rxnorm": "617314"},
    {"name": "Gabapentin", "dose": "300 mg", "rxnorm": "1973610"},
    {"name": "Hydrochlorothiazide", "dose": "25 mg", "rxnorm": "8570"},
    {"name": "Furosemide", "dose": "40 mg", "rxnorm": "3094"},
    {"name": "Azithromycin", "dose": "250 mg", "rxnorm": "3095"},
    {"name": "Prednisone", "dose": "10 mg", "rxnorm": "8640"},
]

LAB_TESTS = [
    {"loinc": "718-7", "desc": "Hemoglobin [Mass/volume] in Blood"},
    {"loinc": "2345-7", "desc": "Glucose [Mass/volume] in Blood"},
    {"loinc": "4548-4", "desc": "Hemoglobin A1c/Hemoglobin.total in Blood"},
    {"loinc": "2093-3", "desc": "Cholesterol [Mass/volume] in Serum or Plasma"},
    {"loinc": "24323-8", "desc": "TSH [Units/volume] in Serum or Plasma"},
    {"loinc": "6690-2", "desc": "Leukocytes [#/volume] in Blood (WBC)"},
    {"loinc": "777-3", "desc": "Platelets [#/volume] in Blood"},
    {"loinc": "2160-0", "desc": "Creatinine [Mass/volume] in Serum or Plasma"},
    {"loinc": "3094-0", "desc": "Urea nitrogen [Mass/volume] in Serum or Plasma (BUN)"},
    {"loinc": "2951-2", "desc": "Sodium [Moles/volume] in Serum or Plasma"},
    {"loinc": "2823-3", "desc": "Potassium [Moles/volume] in Serum or Plasma"},
    {"loinc": "1742-6", "desc": "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma (ALT)"},
    {"loinc": "1920-8", "desc": "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma (AST)"},
    {"loinc": "1975-2", "desc": "Bilirubin.total [Mass/volume] in Serum or Plasma"},
    {"loinc": "1988-5", "desc": "C reactive protein [Mass/volume] in Serum or Plasma (CRP)"},
]

IMAGING_MODALITIES = ["XR", "CT", "MRI", "US"]

ALLERGY_TYPES = [
    {"substance": "Peanut", "reaction": "Anaphylaxis"},
    {"substance": "Penicillin", "reaction": "Rash"},
    {"substance": "Latex", "reaction": "Contact dermatitis"},
]

DOCUMENT_TYPES = [
    {"type": "Discharge Summary", "format": "text/plain"},
    {"type": "Operative Note", "format": "text/plain"},
    {"type": "Consult Note", "format": "text/plain"},
]

CHRONIC_CONDITIONS = [
    {"code": "44054006", "desc": "Diabetes mellitus type 2", "tag": "diabetes"},
    {"code": "38341003", "desc": "Hypertensive disorder", "tag": "hypertension"},
    {"code": "55822004", "desc": "Hyperlipidemia", "tag": "hyperlipidemia"},
    {"code": "195967001", "desc": "Asthma", "tag": "asthma"},
    {"code": "35489007", "desc": "Depressive disorder", "tag": "depression"},
]

LAB_RANGES = {
    "718-7":  {"min": 11.0, "max": 16.0, "unit": "g/dL", "code": "g/dL"},
    "2345-7": {"min": 70.0, "max": 140.0, "unit": "mg/dL", "code": "mg/dL"},
    "4548-4": {"min": 4.0, "max": 10.0, "unit": "%", "code": "%"},
    "2093-3": {"min": 120.0, "max": 240.0, "unit": "mg/dL", "code": "mg/dL"},
    "24323-8": {"min": 0.4, "max": 4.0, "unit": "uIU/mL", "code": "uIU/mL"},
    "6690-2": {"min": 4.0, "max": 11.0, "unit": "10^3/uL", "code": "10*3/uL"},
    "777-3": {"min": 150.0, "max": 400.0, "unit": "10^3/uL", "code": "10*3/uL"},
    "2160-0": {"min": 0.6, "max": 1.3, "unit": "mg/dL", "code": "mg/dL"},
    "3094-0": {"min": 7.0, "max": 20.0, "unit": "mg/dL", "code": "mg/dL"},
    "2951-2": {"min": 135.0, "max": 145.0, "unit": "mmol/L", "code": "mmol/L"},
    "2823-3": {"min": 3.5, "max": 5.1, "unit": "mmol/L", "code": "mmol/L"},
    "1742-6": {"min": 7.0, "max": 56.0, "unit": "U/L", "code": "U/L"},
    "1920-8": {"min": 10.0, "max": 40.0, "unit": "U/L", "code": "U/L"},
    "1975-2": {"min": 0.1, "max": 1.2, "unit": "mg/dL", "code": "mg/dL"},
    "1988-5": {"min": 0.0, "max": 10.0, "unit": "mg/L", "code": "mg/L"},
}


# -------------------------------------------------------------------
# Utility helpers
# -------------------------------------------------------------------
def random_date_in_year(year: int) -> datetime:
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    delta = end - start
    offset = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=offset)


def random_birthdate(min_year: int = 1940, max_year: int = 2020) -> str:
    year = random.randint(min_year, max_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(year, month, day).date().isoformat()


def age_at(patient: Dict[str, Any], encounter: Dict[str, Any]) -> float:
    dob = datetime.fromisoformat(patient["birthDate"])
    enc_start = datetime.fromisoformat(encounter["period"]["start"])
    return (enc_start.date() - dob.date()).days / 365.25


def write_fhir(resource: Dict[str, Any], path: str) -> str:
    if path is None:
        raise ValueError("write_fhir received None path")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resource, f, indent=2)
    return path


def rand_alnum(length: int) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def gen_id(n_digits: int = 5) -> str:
    return str(uuid.uuid4())[:n_digits]


def gen_mrn() -> str:
    return gen_id()


def gen_encounter_id() -> str:
    return gen_id()


def random_datetime_within_year(year: int) -> str:
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31, 23, 59, 59)
    delta = end - start
    rand_seconds = random.randint(0, int(delta.total_seconds()))
    dt = start + timedelta(seconds=rand_seconds)
    return dt.isoformat()


def safe_filename(*parts) -> str:
    name = "_".join(str(p) for p in parts if p is not None and p != "")
    for ch in [":", "/", "\\", " ", ","]:
        name = name.replace(ch, "-")
    if len(name) > 200:
        name = name[:200]
    name = f"{name}.json"
    return name


def delete_all_files(out_dir, endswith_str=".json"):
    try:
        for filename in os.listdir(out_dir):
            if filename.endswith(endswith_str):
                file_path = os.path.join(out_dir, filename)
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                except Exception as e:
                    print(f"{e}")
    except Exception as e:
        print(f"{e}")


def remove_directory(path: str):
    if not path:
        raise ValueError("Path is empty or None")

    if not os.path.exists(path):
        print(f"Directory does not exist: {path}")
        return

    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")

    shutil.rmtree(path)
    print(f"Removed directory: {path}")


# -------------------------------------------------------------------
# FHIRPath-like invariants (simple Python checks)
# -------------------------------------------------------------------
FHIRPATH_INVARIANTS: Dict[str, List[Dict[str, Any]]] = {
    "Encounter": [
        {
            "name": "enc-subject",
            "fhirpath": "subject.exists()",
            "check": lambda r: r.get("subject") is not None,
        },
        {
            "name": "enc-period-start",
            "fhirpath": "period.start.exists()",
            "check": lambda r: bool(r.get("period") and r["period"].get("start")),
        },
    ],
    "Observation": [
        {
            "name": "obs-code",
            "fhirpath": "code.coding.exists()",
            "check": lambda r: bool(r.get("code") and r["code"].get("coding")),
        },
        {
            "name": "obs-subject",
            "fhirpath": "subject.exists()",
            "check": lambda r: r.get("subject") is not None,
        },
    ],
    "MedicationRequest": [
        {
            "name": "medreq-medication",
            "fhirpath": "medication.exists()",
            "check": lambda r: bool(r.get("medicationCodeableConcept")),
        },
        {
            "name": "medreq-subject",
            "fhirpath": "subject.exists()",
            "check": lambda r: r.get("subject") is not None,
        },
    ],
}


def evaluate_invariants(resource: Dict[str, Any]) -> List[Dict[str, Any]]:
    if resource is None:
        return [{"error": "resource is None"}]
    rtype = resource.get("resourceType")
    if not rtype:
        return [{"error": f"invalid resource type: {type(resource)}"}]

    results: List[Dict[str, Any]] = []
    for inv in FHIRPATH_INVARIANTS.get(rtype, []):
        ok = False
        try:
            ok = bool(inv["check"](resource))
        except Exception:
            ok = False
        results.append(
            {
                "resourceType": rtype,
                "id": resource.get("id"),
                "invariant": inv["name"],
                "fhirpath": inv["fhirpath"],
                "ok": ok,
            }
        )
    return results


# -------------------------------------------------------------------
# Resource generators (dict-based)
# -------------------------------------------------------------------
def make_patient(mrn: str, profiles: dict) -> Dict[str, Any]:
    given = faker.first_name()
    family = faker.last_name()
    gender = random.choice(["male", "female", "other", "unknown"])
    birth_date = faker.date_of_birth(minimum_age=0, maximum_age=95).isoformat()

    race_text = random.choice(
        ["White", "Black or African American", "Asian", "Hispanic or Latino", "Other"]
    )
    ethnicity_text = random.choice(["Not Hispanic or Latino", "Hispanic or Latino"])

    identifiers = [
        {
            # Synthetic MRN — use a realistic hospital namespace 
            # Used widely in SMART-on-FHIR examples; safe, synthetic, non‑resolvable.
            "system": "http://hospital.smarthealthit.org/mrn",
            "value": mrn,
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "MR",
                        "display": "Medical record number",
                    }
                ]
            },
        },
        {   # SSN-like identifier — use official US Core SID 
            # This is the official FHIR namespace for SSNs.
            "system": "http://hl7.org/fhir/sid/us-ssn",            
            "value": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "SS",
                        "display": "Social Security Number",
                    }
                ]
            },
        },
    ]

    telecom = [
        {"system": "phone", "value": faker.phone_number(), "use": "mobile"},
        {"system": "email", "value": faker.safe_email(), "use": "home"},
    ]

    address = [
        {
            "use": "home",
            "line": [faker.street_address()],
            "city": faker.city(),
            "state": faker.state_abbr(),
            "postalCode": faker.postcode(),
            "country": "US",
        }
    ]

    contact = [
        {
            "relationship": [{"text": "emergency"}],
            "name": {
                "family": faker.last_name(),
                "given": [faker.first_name()],
            },
            "telecom": [
                {"system": "phone", "value": faker.phone_number(), "use": "home"}
            ],
        }
    ]

    communication = [
        {
            "language": {"text": "English"},
            "preferred": True,
        }
    ]

    patient = {
        "resourceType": "Patient",
        "id": gen_id(),
        "meta": uscore_meta(profiles["PATIENT"]),
        "identifier": identifiers,
        "name": [{"use": "official", "family": family, "given": [given]}],
        "gender": gender,
        "birthDate": birth_date,
        "telecom": telecom,
        "address": address,
        "contact": contact,
        "communication": communication,
        "extension": [
            {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                "valueCodeableConcept": {"text": race_text},
            },
            {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                "valueCodeableConcept": {"text": ethnicity_text},
            },
        ],
    }

    return patient


def make_chronic_conditions(
    patient: Dict[str, Any],
    mrn: str,
    profiles: dict,
    n_min: int = 0,
    n_max: int = 3,
) -> List[Dict[str, Any]]:
    rnd = random.Random(mrn)
    n = rnd.randint(n_min, n_max)
    chosen = rnd.sample(CHRONIC_CONDITIONS, k=n) if n > 0 else []
    conds: List[Dict[str, Any]] = []

    for c in chosen:
        conds.append(
            {
                "resourceType": "Condition",
                "id": gen_id(),
                "meta": uscore_meta(profiles["CONDITION"]),
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active",
                        }
                    ]
                },
                "verificationStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                            "code": "confirmed",
                        }
                    ]
                },
                "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": c["code"],
                            "display": c["desc"],
                        }
                    ]
                },
                "subject": {"reference": f"Patient/{patient['id']}"},
            }
        )
    return conds


def make_encounter(
    patient: Dict[str, Any],
    year: int,
    profiles: dict,
) -> Dict[str, Any]:
    start_dt = random_date_in_year(year).replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(hours=random.randint(1, 24 * 5))

    start_str = start_dt.isoformat()
    end_str = end_dt.isoformat()

    reason_label, reason_code = random.choice(
        [
            ("Chest pain", "29857009"),
            ("Pre-op evaluation", "30549001"),
            ("Infection", "40733004"),
            ("Follow-up", "185389009"),
            ("Trauma", "417163006"),
        ]
    )

    reason_cc = {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": reason_code,
                "display": reason_label,
            }
        ],
        "text": reason_label,
    }

    type_label, type_code = random.choice(
        [
            ("Office Visit", "185349003"),
            ("Emergency Department Visit", "50849002"),
            ("Surgical Follow-up", "30549001"),
            ("Consultation", "11429006"),
        ]
    )

    type_cc = {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": type_code,
                "display": type_label,
            }
        ],
        "text": type_label,
    }

    location_name = random.choice(["ER", "OR", "Clinic", "Ward B"])
    location_ref = f"Location/{location_name.replace(' ', '').lower()}"

    encounter_location = {
        "location": {
            "reference": location_ref,
            "display": location_name,
        }
    }

    enc = {
        "resourceType": "Encounter",
        "id": gen_id(),
        "meta": uscore_meta(profiles["ENCOUNTER"]),
        "status": "finished",
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": "AMB",
            "display": "ambulatory",
        },
        "type": [type_cc],
        "subject": {"reference": f"Patient/{patient['id']}"},
        "period": {"start": start_str, "end": end_str},
        "reasonCode": [reason_cc],
        "location": [encounter_location],
    }

    return enc


def make_procedures(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    profiles: dict,
    n_min: int = 0,
    n_max: int = 2,
) -> List[Dict[str, Any]]:

    n = random.randint(n_min, n_max)
    procs: List[Dict[str, Any]] = []

    for _ in range(n):
        surgery = random.choice(SURGERIES)

        # Performed datetime (US Core allows performedDateTime or performedPeriod)
        performed = random_datetime_within_year(
            datetime.fromisoformat(enc["period"]["start"]).year
        )

        # Practitioner reference
        practitioner_id = f"pract-{rand_alnum(6)}"

        proc = {
            "resourceType": "Procedure",
            "id": gen_id(),
            "meta": uscore_meta(profiles["PROCEDURE"]),

            "status": "completed",

            # US Core requires SNOMED CT coding
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": surgery["code"],
                    "display": surgery["desc"]
                }],
                "text": surgery["desc"]
            },

            "subject": {"reference": f"Patient/{patient['id']}"},

            # US Core allows performedDateTime
            "performedDateTime": performed,

            # US Core requires performer.actor to be a Reference
            "performer": [{
                "actor": {
                    "reference": f"Practitioner/{practitioner_id}",
                    "display": faker.name()
                }
            }],

            # US Core recommends encounter linkage
            "encounter": {"reference": f"Encounter/{enc['id']}"},

            # Optional but valid and helpful
            "category": [{
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "387713003",  # "Surgical procedure"
                    "display": "Surgical procedure"
                }]
            }],

            "note": [{
                "text": f"Operative note: {surgery['desc']}. No complications."
            }],
        }

        procs.append(proc)

    return procs


def make_allergies(
    patient: Dict[str, Any],
    profiles: dict,
    n_min: int = 0,
    n_max: int = 2,
) -> List[Dict[str, Any]]:
    n = random.randint(n_min, n_max)
    alls: List[Dict[str, Any]] = []

    for a in random.sample(ALLERGY_TYPES, k=n):
        manifestation = {
            "concept": {
                "text": a["reaction"],
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "271807003",
                        "display": a["reaction"],
                    }
                ],
            }
        }

        allergy = {
            "resourceType": "AllergyIntolerance",
            "id": gen_id(),
            "meta": uscore_meta(profiles["ALLERGY"]),
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": "confirmed",
                    }
                ]
            },
            "code": {
                "text": a["substance"],
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "91936005",
                        "display": a["substance"],
                    }
                ],
            },
            "patient": {"reference": f"Patient/{patient['id']}"},
            "reaction": [
                {
                    "manifestation": [manifestation],
                }
            ],
        }

        alls.append(allergy)

    return alls


def make_document_reference(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    profiles: dict,
    procedures: Optional[List[Dict[str, Any]]] = None,
    n_min: int = 0,
    n_max: int = 2,
) -> List[Dict[str, Any]]:

    # Map synthetic document types → LOINC codes
    loinc_map = {
        "Discharge Summary": "18842-5",
        "Operative Note": "11504-8",
        "Consult Note": "11488-4",
    }

    year = datetime.fromisoformat(enc["period"]["start"]).year

    n_docs = random.randint(n_min, n_max)
    docs: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # Generate general clinical notes
    # ---------------------------------------------------------
    for d in random.sample(DOCUMENT_TYPES, k=n_docs):

        loinc_code = loinc_map.get(d["type"], "34133-9")  # fallback: clinical note

        doc = {
            "resourceType": "DocumentReference",
            "id": gen_id(),

            "meta": uscore_meta(profiles["DOCREF"]),

            "status": "current",

            # Required by US Core
            "category": [{
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "34133-9",
                    "display": "Summarization of Episode Note"
                }]
            }],

            # Required by US Core
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": loinc_code,
                    "display": d["type"]
                }],
                "text": d["type"]
            },

            "subject": {"reference": f"Patient/{patient['id']}"},

            # Recommended by US Core
            "date": random_datetime_within_year(year),

            "content": [{
                "attachment": {
                    "contentType": d["format"],
                    "title": f"Synthetic {d['type']}",
                    # US Core–aligned synthetic binary URL 
                    "url": f"https://hl7.org/fhir/us/core/Binary/{rand_alnum(12)}"
                }
            }],

            "description": f"Synthetic {d['type']}.",

            "context": {
                "encounter": [{"reference": f"Encounter/{enc['id']}"}],
                "period": {
                    "start": random_datetime_within_year(year)
                }
            }
        }

        docs.append(doc)

    # ---------------------------------------------------------
    # Generate operative notes linked to Procedures
    # ---------------------------------------------------------
    if procedures:
        for proc in procedures:

            loinc_code = loinc_map.get("Operative Note", "11504-8")

            op_note = {
                "resourceType": "DocumentReference",
                "id": gen_id(),

                "meta": uscore_meta(profiles["DOCREF"]),

                "status": "current",

                "category": [{
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "34133-9",
                        "display": "Summarization of Episode Note"
                    }]
                }],

                "type": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": loinc_code,
                        "display": "Operative Note"
                    }],
                    "text": "Operative Note"
                },

                "subject": {"reference": f"Patient/{patient['id']}"},

                "date": random_datetime_within_year(year),

                "relatesTo": [{
                    "code": "documents",
                    "target": {"reference": f"Procedure/{proc['id']}"}
                }],

                "content": [{
                    "attachment": {
                        "contentType": "text/plain",
                        "title": f"Operative Note for {proc['code']['coding'][0]['display']}",
                        # US Core–aligned synthetic binary URL 
                        "url": f"https://hl7.org/fhir/us/core/Binary/{rand_alnum(12)}"
                    }
                }],

                "description": f"Synthetic operative note for {proc['code']['coding'][0]['display']}.",

                "context": {
                    "encounter": [{"reference": f"Encounter/{enc['id']}"}],
                    "period": {
                        "start": random_datetime_within_year(year)
                    }
                }
            }

            docs.append(op_note)

    return docs


def make_medication_requests(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    conditions: List[Dict[str, Any]],
    profiles: dict,
    n_min: int = 0,
    n_max: int = 2,
) -> List[Dict[str, Any]]:

    # Map chronic conditions → preferred medications
    tag_to_meds = {
        "diabetes": ["Metformin"],
        "hyperlipidemia": ["Atorvastatin", "Simvastatin"],
        "hypertension": ["Lisinopril", "Amlodipine", "Hydrochlorothiazide"],
        "asthma": ["Albuterol"],
        "depression": ["Sertraline"],
    }

    # Condition references for reasonReference
    reason_refs = [{"reference": f"Condition/{c['id']}"} for c in conditions]

    # Determine chronic-condition-driven medications
    chosen_meds: List[Dict[str, Any]] = []
    for c in conditions:
        code = c["code"]["coding"][0]["code"]
        tag = next((cc["tag"] for cc in CHRONIC_CONDITIONS if cc["code"] == code), None)
        if tag and tag in tag_to_meds:
            for name in tag_to_meds[tag]:
                m = next((mm for mm in MEDICATIONS if mm["name"] == name), None)
                if m:
                    chosen_meds.append(m)

    # Add acute medications
    acute_pool = [m for m in MEDICATIONS if m["name"] not in {cm["name"] for cm in chosen_meds}]
    for m in random.sample(acute_pool, k=random.randint(n_min, n_max)):
        chosen_meds.append(m)

    meds: List[Dict[str, Any]] = []

    # Build MedicationRequest resources
    for m in chosen_meds:

        # Practitioner requester
        requester_id = f"prac-{rand_alnum(6)}"

        # AuthoredOn based on encounter year
        year = datetime.fromisoformat(enc["period"]["start"]).year
        authored_on = random_datetime_within_year(year)

        med = {
            "resourceType": "MedicationRequest",
            "id": gen_id(),
            "meta": uscore_meta(profiles["MEDREQ"]),

            "status": "active",
            "intent": "order",

            # Medication coding + text (added from build_medication_request)
            "medicationCodeableConcept": {
                "text": m["name"],
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": m["rxnorm"],
                        "display": f"{m['name']} {m['dose']}",
                    }
                ],
            },

            "subject": {"reference": f"Patient/{patient['id']}"},
            "encounter": {"reference": f"Encounter/{enc['id']}"},

            # AuthoredOn (improved)
            "authoredOn": authored_on,

            # DosageInstruction (added)
            "dosageInstruction": [{
                "text": f"{m['dose']}, take as directed",
                "timing": {
                    "repeat": {
                        "frequency": 1,
                        "period": 24,
                        "periodUnit": "h"
                    }
                }
            }],

            # Requester (added)
            "requester": {
                "reference": f"Practitioner/{requester_id}"
            },
        }

        # Add reasonReference if available
        if reason_refs:
            med["reasonReference"] = random.sample(reason_refs, k=min(1, len(reason_refs)))

        meds.append(med)

    return meds


def make_medication_documents(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    meds: List[Dict[str, Any]],
    profiles: dict,
) -> List[Dict[str, Any]]:
    if not meds:
        return []

    doc = {
        "resourceType": "DocumentReference",
        "id": gen_id(),
        "meta": uscore_meta(profiles["DOCREF"]),
        "status": "current",
        "type": {"text": "Medication List"},
        "subject": {"reference": f"Patient/{patient['id']}"},
        "context": {
            "encounter": [{"reference": f"Encounter/{enc['id']}"}],
        },
        "relatesTo": [
            {"code": "documents", "target": {"reference": f"MedicationRequest/{m['id']}"}}
            for m in meds
        ],
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "url": f"urn:uuid:{uuid.uuid4()}",
                    "title": "Medication List",
                }
            }
        ],
    }
    return [doc]


def make_immunizations(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    profiles: dict,
) -> List[Dict[str, Any]]:
    age = age_at(patient, enc)

    pediatric = [i for i in IMMUNIZATIONS if i["vaccine"] in {"MMR", "Varicella", "Rotavirus"}]
    adolescent = [i for i in IMMUNIZATIONS if i["vaccine"] in {"HPV", "Tdap"}]
    adult_core = [i for i in IMMUNIZATIONS if i["vaccine"] in {"Influenza", "COVID-19", "Hepatitis B"}]
    older_adult = [i for i in IMMUNIZATIONS if i["vaccine"] in {"Pneumococcal Conjugate (PCV13)"}]

    candidates: List[dict] = []
    if age < 5:
        candidates += pediatric + adult_core
    elif 5 <= age < 18:
        candidates += pediatric + adolescent + adult_core
    elif 18 <= age < 65:
        candidates += adult_core + adolescent
    else:
        candidates += adult_core + older_adult

    if not candidates:
        return []

    n = random.randint(0, min(3, len(candidates)))
    if n == 0:
        return []

    imms: List[Dict[str, Any]] = []
    for imm in random.sample(candidates, k=n):
        imms.append(
            {
                "resourceType": "Immunization",
                "id": gen_id(),
                "meta": uscore_meta(profiles["IMMUNIZATION"]),
                "status": "completed",
                "vaccineCode": {
                    "coding": [
                        {
                            "system": "http://hl7.org/fhir/sid/cvx",
                            "code": imm["cvx"],
                            "display": imm["vaccine"],
                        }
                    ]
                },
                "patient": {"reference": f"Patient/{patient['id']}"},
                "encounter": {"reference": f"Encounter/{enc['id']}"},
                "occurrenceDateTime": enc["period"]["start"],
            }
        )
    return imms


def make_labs(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    conditions: List[Dict[str, Any]],
    profiles: dict,
    n_min: int = 0,
    n_max: int = 5,
) -> List[Dict[str, Any]]:
    n = random.randint(n_min, n_max)
    chosen = random.sample(LAB_TESTS, k=n) if n > 0 else []

    cond_codes = {c["code"]["coding"][0]["code"] for c in conditions}
    has_diabetes = "44054006" in cond_codes
    has_hyperlipidemia = "55822004" in cond_codes

    if has_diabetes:
        for loinc in ["2345-7", "4548-4"]:
            if not any(l["loinc"] == loinc for l in chosen):
                chosen.append(next(l for l in LAB_TESTS if l["loinc"] == loinc))

    if has_hyperlipidemia:
        loinc = "2093-3"
        if not any(l["loinc"] == loinc for l in chosen):
            chosen.append(next(l for l in LAB_TESTS if l["loinc"] == loinc))

    obs: List[Dict[str, Any]] = []
    for lab in chosen:
        loinc = lab["loinc"]
        meta = LAB_RANGES.get(loinc, {"min": 1.0, "max": 100.0, "unit": "arb", "code": "1"})
        value = round(random.uniform(meta["min"], meta["max"]), 2)

        obs.append(
            {
                "resourceType": "Observation",
                "id": gen_id(),
                "meta": uscore_meta(profiles["LAB_OBS"]),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "laboratory",
                                "display": "Laboratory",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": loinc,
                            "display": lab["desc"],
                        }
                    ]
                },
                "subject": {"reference": f"Patient/{patient['id']}"},
                "encounter": {"reference": f"Encounter/{enc['id']}"},
                "effectiveDateTime": enc["period"]["start"],
                "valueQuantity": {
                    "value": value,
                    "unit": meta["unit"],
                    "system": "http://unitsofmeasure.org",
                    "code": meta["code"],
                },
            }
        )
    return obs


def make_diagnostic_report(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    observations: List[Dict[str, Any]],
    profiles: dict,
) -> Optional[Dict[str, Any]]:

    # If no external observations exist, skip
    if not observations:
        return None

    # Encounter year for synthetic timestamps
    year = datetime.fromisoformat(enc["period"]["start"]).year

    # -----------------------------
    # Build contained Observations
    # -----------------------------
    n_tests = random.randint(2, 10)
    chosen_tests = (
        random.sample(LAB_TESTS, k=n_tests)
        if n_tests <= len(LAB_TESTS)
        else [random.choice(LAB_TESTS) for _ in range(n_tests)]
    )

    contained = []
    result_refs = []

    def _plausible_value_for_loinc(loinc: str, desc: str):
        d = desc.lower()
        if "a1c" in d:
            return {"valueQuantity": {"value": round(random.uniform(4.5, 10.0), 1), "unit": "%", "system": "http://unitsofmeasure.org"}}
        if "hemoglobin" in d and "a1c" not in d:
            return {"valueQuantity": {"value": round(random.uniform(11.0, 17.5), 1), "unit": "g/dL", "system": "http://unitsofmeasure.org"}}
        if "glucose" in d:
            return {"valueQuantity": {"value": round(random.uniform(65, 200), 1), "unit": "mg/dL", "system": "http://unitsofmeasure.org"}}
        if "cholesterol" in d:
            return {"valueQuantity": {"value": round(random.uniform(120, 300), 1), "unit": "mg/dL", "system": "http://unitsofmeasure.org"}}
        if "tsh" in d:
            return {"valueQuantity": {"value": round(random.uniform(0.1, 8.0), 2), "unit": "uIU/mL", "system": "http://unitsofmeasure.org"}}
        if "leukocytes" in d or "wbc" in d:
            return {"valueQuantity": {"value": round(random.uniform(3.0, 12.0), 1), "unit": "10^3/uL", "system": "http://unitsofmeasure.org"}}
        if "platelet" in d:
            return {"valueQuantity": {"value": round(random.uniform(150, 450), 0), "unit": "10^3/uL", "system": "http://unitsofmeasure.org"}}
        if "creatinine" in d:
            return {"valueQuantity": {"value": round(random.uniform(0.5, 2.5), 2), "unit": "mg/dL", "system": "http://unitsofmeasure.org"}}
        if "urea" in d or "bun" in d:
            return {"valueQuantity": {"value": round(random.uniform(7, 25), 1), "unit": "mg/dL", "system": "http://unitsofmeasure.org"}}
        if "sodium" in d:
            return {"valueQuantity": {"value": round(random.uniform(135, 148), 1), "unit": "mmol/L", "system": "http://unitsofmeasure.org"}}
        if "potassium" in d:
            return {"valueQuantity": {"value": round(random.uniform(3.2, 5.5), 2), "unit": "mmol/L", "system": "http://unitsofmeasure.org"}}
        if "alanine" in d or "alt" in d:
            return {"valueQuantity": {"value": round(random.uniform(7, 56), 1), "unit": "U/L", "system": "http://unitsofmeasure.org"}}
        if "aspartate" in d or "ast" in d:
            return {"valueQuantity": {"value": round(random.uniform(10, 40), 1), "unit": "U/L", "system": "http://unitsofmeasure.org"}}
        if "bilirubin" in d:
            return {"valueQuantity": {"value": round(random.uniform(0.1, 1.5), 2), "unit": "mg/dL", "system": "http://unitsofmeasure.org"}}
        if "crp" in d:
            return {"valueQuantity": {"value": round(random.uniform(0.1, 10.0), 2), "unit": "mg/L", "system": "http://unitsofmeasure.org"}}
        return {"valueQuantity": {"value": round(random.uniform(1.0, 100.0), 2), "unit": "units", "system": "http://unitsofmeasure.org"}}

    # Build contained Observations
    for test in chosen_tests:
        loinc = test["loinc"].replace("/", "-")
        obs_id = f"obs-{loinc}-{rand_alnum(4)}"

        obs = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab"
                ]
            },
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": test["loinc"],
                    "display": test["desc"]
                }],
                "text": test["desc"]
            },
            "subject": {"reference": f"Patient/{patient['id']}"},
            "encounter": {"reference": f"Encounter/{enc['id']}"},
            "effectiveDateTime": random_datetime_within_year(year),
        }

        obs.update(_plausible_value_for_loinc(test["loinc"], test["desc"]))

        contained.append(obs)
        result_refs.append({"reference": f"#{obs_id}"})

    # Add external Observation references
    for o in observations:
        result_refs.append({"reference": f"Observation/{o['id']}"})

    # -----------------------------
    # Build DiagnosticReport
    # -----------------------------
    dr = {
        "resourceType": "DiagnosticReport",
        "id": gen_id(),
        "meta": uscore_meta(profiles["DIAG_REPORT"]),
        "status": "final",

        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                "code": "LAB",
                "display": "Laboratory"
            }]
        }],

        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "11502-2",
                "display": "Laboratory report"
            }],
            "text": "Laboratory report"
        },

        "subject": {"reference": f"Patient/{patient['id']}"},
        "encounter": {"reference": f"Encounter/{enc['id']}"},
        "effectiveDateTime": random_datetime_within_year(year),

        "result": result_refs,

        "conclusion": f"Synthetic diagnostic report containing {len(chosen_tests)} lab tests.",
    }

    if contained:
        dr["contained"] = contained

    return dr


def make_imaging_study(
    patient: Dict[str, Any],
    enc: Dict[str, Any],
    n_min: int = 0,
    n_max: int = 2,
) -> List[Dict[str, Any]]:

    n = random.randint(n_min, n_max)
    studies: List[Dict[str, Any]] = []

    # Encounter year for realistic timestamps
    year = datetime.fromisoformat(enc["period"]["start"]).year

    for _ in range(n):
        modality = random.choice(IMAGING_MODALITIES)

        # Synthetic but valid-ish DICOM UID roots
        study_uid = f"1.2.840.113619.{random.randint(100000,999999)}"
        series_uid = f"{study_uid}.{random.randint(1000,9999)}"

        num_instances = random.randint(1, 8)

        # Build instance list
        instances = []
        for i in range(num_instances):
            inst_uid = f"{series_uid}.{i+1}"
            instances.append({
                "uid": inst_uid,
                "sopClass": {
                    "system": "urn:ietf:rfc:3986",
                    "code": "1.2.840.10008.5.1.4.1.1.2"  # CT Image Storage (generic)
                },
                "number": i + 1
            })

        study = {
            "resourceType": "ImagingStudy",
            "id": gen_id(),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-imagingstudy"
                ]
            },

            "status": "available",

            # US Core required
            "subject": {"reference": f"Patient/{patient['id']}"},
            "encounter": {"reference": f"Encounter/{enc['id']}"},

            "started": random_datetime_within_year(year),

            # Required by FHIR ImagingStudy
            "uid": study_uid,
            "numberOfSeries": 1,
            "numberOfInstances": num_instances,

            "modality": [{
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": modality
            }],

            "description": f"Synthetic {modality} imaging study",

            "series": [{
                "uid": series_uid,
                "number": 1,
                "modality": {
                    "system": "http://dicom.nema.org/resources/ontology/DCM",
                    "code": modality
                },
                "numberOfInstances": num_instances,
                "instance": instances
            }]
        }

        studies.append(study)

    return studies


# -------------------------------------------------------------------
# Worker: generate all resources for (year, mrn, out_dir) + Bundle
# -------------------------------------------------------------------
def generate_mrn_data_for_year(task: Tuple[int, str, str, GeneratorConfig]) -> List[List[str]]:
    year, mrn, out_dir, cfg = task
    profiles = build_profile_paths()
    manifest_rows: List[List[str]] = []
    resources_for_bundle: List[Dict[str, Any]] = []
    invariant_results: List[Dict[str, Any]] = []

    try:
        patient = make_patient(mrn, profiles)
        resources_for_bundle.append(patient)
        patient_path = os.path.join(out_dir, safe_filename(year, mrn, "Patient"))
        write_fhir(patient, patient_path)
        manifest_rows.append([patient_path, "Patient", mrn, "", year])
        invariant_results.extend(evaluate_invariants(patient))

        conditions = make_chronic_conditions(patient, mrn, profiles, 0, 3)
        for c in conditions:
            resources_for_bundle.append(c)
            path = os.path.join(out_dir, safe_filename(year, mrn, "Condition", c["id"]))
            write_fhir(c, path)
            manifest_rows.append([path, "Condition", mrn, "", year])
            invariant_results.extend(evaluate_invariants(c))

        allergies = make_allergies(patient, profiles, 0, 2)
        for a in allergies:
            resources_for_bundle.append(a)
            path = os.path.join(out_dir, safe_filename(year, mrn, "AllergyIntolerance", a["id"]))
            write_fhir(a, path)
            manifest_rows.append([path, "AllergyIntolerance", mrn, "", year])
            invariant_results.extend(evaluate_invariants(a))

        n_encounters = random.randint(3, 10)
        for _ in range(n_encounters):
            enc = make_encounter(patient, year, profiles)
            resources_for_bundle.append(enc)
            enc_path = os.path.join(out_dir, safe_filename(year, mrn, "Encounter", enc["id"]))
            write_fhir(enc, enc_path)
            manifest_rows.append([enc_path, "Encounter", mrn, enc["id"], year])
            invariant_results.extend(evaluate_invariants(enc))

            procs = make_procedures(patient, enc, profiles)
            for p in procs:
                resources_for_bundle.append(p)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "Procedure", enc["id"], p["id"]),
                )
                write_fhir(p, path)
                manifest_rows.append([path, "Procedure", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(p))

            docs = make_document_reference(patient, enc, profiles, procedures=procs)
            for d in docs:
                resources_for_bundle.append(d)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "DocumentReference", enc["id"], d["id"]),
                )
                write_fhir(d, path)
                manifest_rows.append([path, "DocumentReference", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(d))

            meds = make_medication_requests(patient, enc, conditions, profiles)
            for m in meds:
                resources_for_bundle.append(m)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "MedicationRequest", enc["id"], m["id"]),
                )
                write_fhir(m, path)
                manifest_rows.append([path, "MedicationRequest", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(m))

            med_docs = make_medication_documents(patient, enc, meds, profiles)
            for d in med_docs:
                resources_for_bundle.append(d)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "DocumentReference", enc["id"], d["id"]),
                )
                write_fhir(d, path)
                manifest_rows.append([path, "DocumentReference", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(d))

            imms = make_immunizations(patient, enc, profiles)
            for im in imms:
                resources_for_bundle.append(im)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "Immunization", enc["id"], im["id"]),
                )
                write_fhir(im, path)
                manifest_rows.append([path, "Immunization", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(im))

            labs = make_labs(patient, enc, conditions, profiles)
            for o in labs:
                resources_for_bundle.append(o)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "Observation", enc["id"], o["id"]),
                )
                write_fhir(o, path)
                manifest_rows.append([path, "Observation", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(o))

            dr = make_diagnostic_report(patient, enc, labs, profiles)
            if dr:
                resources_for_bundle.append(dr)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "DiagnosticReport", enc["id"], dr["id"]),
                )
                write_fhir(dr, path)
                manifest_rows.append([path, "DiagnosticReport", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(dr))

            imgs = make_imaging_study(patient, enc)
            for img in imgs:
                resources_for_bundle.append(img)
                path = os.path.join(
                    out_dir,
                    safe_filename(year, mrn, "ImagingStudy", enc["id"], img["id"]),
                )
                write_fhir(img, path)
                manifest_rows.append([path, "ImagingStudy", mrn, enc["id"], year])
                invariant_results.extend(evaluate_invariants(img))

        bundle = {
            "resourceType": "Bundle",
            "id": gen_id(),
            "type": "collection",
            "entry": [{"resource": r} for r in resources_for_bundle],
        }
        bundle_path = os.path.join(out_dir, safe_filename(year, mrn, "Bundle"))
        write_fhir(bundle, bundle_path)
        manifest_rows.append([bundle_path, "Bundle", mrn, "", year])

        inv_path = os.path.join(out_dir, safe_filename(year, mrn, "invariants"))
        with open(inv_path, "w", encoding="utf-8") as f:
            json.dump(invariant_results, f, indent=2)
        manifest_rows.append([inv_path, "InvariantResults", mrn, "", year])

        return manifest_rows

    except Exception as e:
        print(f"Worker error for MRN {mrn} year {year}: {e}")
        return []


import re

ANSI_ESCAPE = re.compile(r"\x1B\[[0-9;]*[A-Za-z]")

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text or "")



# -------------------------------------------------------------------
# Validation using HL7 FHIR validator CLI JAR + local US Core package
# -------------------------------------------------------------------
def validate_manifest(
    manifest_rows: List[List[str]],
    validator_jar: Optional[str] = None,
    uscore_root: str = None,
    #profiles: Optional[dict] = None,
    out_dir: str = None,
) -> List[Dict[str, Any]]:
    """
    Run HL7 FHIR validator CLI against each generated resource.
    Writes results incrementally to validation_results.json
    while preserving correct JSON array structure.
    """

    if not validator_jar:
        print("No validator_jar configured; skipping external validation.")
        return []

    # if not profiles:
    #     print("No profiles provided; skipping external validation.")
    #     return []

    if out_dir is None:
        out_dir = os.getcwd()

    # Output file path
    results_path = os.path.join(out_dir, "validation_results.json")
    print(f"Streaming validation results to: {results_path}")

    # Open file and begin JSON array
    f = open(results_path, "w", encoding="utf-8")
    f.write("[\n")   # start JSON array
    first = True      # track commas

    # Determine IG folder
    #uscore_root = os.path.dirname(list(profiles.values())[0])
    ig_arg = os.path.dirname(uscore_root)

    results: List[Dict[str, Any]] = []

    for row in manifest_rows:
        filepath, rtype, mrn, enc_id, year = row

        if not os.path.isfile(filepath):
            continue

        cmd = [
            "java",
            "-jar",
            validator_jar,
            filepath,
            "-version",
            "4.0.1",
            "-ig",
            ig_arg,
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            ok = proc.returncode == 0

            # -----------------------------------------
            # Clean ANSI escape codes
            # -----------------------------------------
            clean_stdout = strip_ansi(proc.stdout)
            clean_stderr = strip_ansi(proc.stderr)
            
            # -----------------------------------------
            # The FHIR validator prints *errors* to stdout,
            # not stderr. So we must extract them from stdout.
            # -----------------------------------------
            stdout_lines = clean_stdout.splitlines()
            
            error_lines = [
                line for line in stdout_lines
                if "error" in line.lower() or "*failure*" in line.lower()
            ]
            
            non_error_lines = [
                line for line in stdout_lines
                if "error" not in line.lower() and "*failure*" not in line.lower()
            ]
            
            # -----------------------------------------
            # stderr = ONLY errors
            # stdout = everything else (stdout + stderr)
            # -----------------------------------------
            filtered_stderr = "\n".join(error_lines)
            
            # stdout gets:
            #   - non-error stdout
            #   - all of stderr (warnings, stack traces)
            filtered_stdout = "\n".join(non_error_lines)
            if clean_stderr.strip():
                filtered_stdout += "\n" + clean_stderr.strip() + "\n"
            
            result = {
                "file": filepath,
                "resourceType": rtype,
                "mrn": mrn,
                "encounter_id": enc_id,
                "year": year,
                "ok": ok,
                "returncode": proc.returncode,
                "stdout": filtered_stdout,
                "stderr": filtered_stderr,
            }

        except Exception as e:
            result = {
                "file": filepath,
                "resourceType": rtype,
                "mrn": mrn,
                "encounter_id": enc_id,
                "year": year,
                "ok": False,
                "error": str(e),
            }

        # Add to in-memory list

        results.append(result)

        # Stream to file with proper JSON formatting
        if not first:
            f.write(",\n")
        f.write(json.dumps(result, indent=2))
        first = False

        f.flush()

    # Close JSON array
    f.write("\n]\n")
    f.close()

    return results


def generate_summary(
    manifest_rows: List[List[str]],
    validation_results: List[Dict[str, Any]],
    out_root_dir: str,
):
    totals = {
        "files": len(manifest_rows),
        "patients": len({r[2] for r in manifest_rows if r[1] == "Patient"}),
        "encounters": len({r[3] for r in manifest_rows if r[1] == "Encounter"}),
    }

    valid = sum(1 for r in validation_results if r.get("ok"))
    invalid = sum(1 for r in validation_results if r.get("ok") is False and "error" not in r)
    errors = sum(1 for r in validation_results if "error" in r)

    summary = {
        "totals": totals,
        "validation": {
            "valid": valid,
            "valid_structural": 0,  # not distinguished here
            "invalid": invalid,
            "errors": errors,
        },
    }

    summary_json_path = os.path.join(out_root_dir, "summary.json")
    summary_csv_path = os.path.join(out_root_dir, "summary.csv")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in summary["totals"].items():
            w.writerow([k, v])
        for k, v in summary["validation"].items():
            w.writerow([f"validation_{k}", v])
    return summary_json_path, summary_csv_path, summary


# # ---------------------------------------------------------
# # Check validator availability BEFORE attempting validation
# # ---------------------------------------------------------
# def validator_available(path: str) -> bool:
#     if not path:
#         print("No validator JAR path provided. Skipping validation.")
#         return False

#     if not os.path.isfile(path):
#         print(f"Validator JAR not found at: {path}")
#         print("Skipping validation.")
#         return False

#     # Try running `java -jar validator.jar help` to confirm it works
#     try:
#         test_cmd = ["java", "-jar", path, "-help"]
#         proc = subprocess.run(
#             test_cmd,
#             capture_output=True,
#             text=True,
#             timeout=5,
#             check=False
#         )
#         if proc.returncode != 0:
#             print("Validator JAR exists but could not be executed.")
#             print("Skipping validation.")
#             return False
#     except Exception as e:
#         print(f"Validator JAR execution failed: {e}")
#         print("Skipping validation.")
#         return False

#     return True


# -------------------------------------------------------------------
# Top-level driver
# -------------------------------------------------------------------
def run_generation(cfg: GeneratorConfig):

    if cfg.seed is not None:
        random.seed(cfg.seed)
        Faker.seed(cfg.seed)

    out_root_dir = cfg.out_root_dir
    # Remove all contents of out_root_dir
    #if getattr(cfg, "remove_existing_files", 0) == 1:
    if cfg.remove_existing_files == 1:
        print(f"Removing contents of {out_root_dir}")
        remove_directory(out_root_dir)

    out_data_dir = os.path.join(out_root_dir, "data")
    manifest_file = "manifest.csv"

    os.makedirs(out_data_dir, exist_ok=True)

    tasks = []
    for year in range(cfg.start_year, cfg.end_year + 1):
        for _ in range(cfg.mrns_per_year):
            mrn = gen_mrn()
            tasks.append((year, mrn, out_data_dir, cfg))

    total_tasks = len(tasks)
    print(
        f"Generating {total_tasks} MRN-year tasks using {cfg.workers} workers "
        f"(chunksize={cfg.chunksize})..."
    )

    results = []
    with Pool(processes=cfg.workers) as pool:
        for worker_result in pool.imap_unordered(generate_mrn_data_for_year, tasks, chunksize=cfg.chunksize):
            if worker_result is None:
                print("Warning: worker returned None; skipping.")
                continue
            if isinstance(worker_result, (list, tuple)):
                results.append(worker_result)
            else:
                print(f"Warning: worker returned unexpected type {type(worker_result)}; skipping.")
                continue

    manifest_rows_flat = [row for sub in results for row in sub]

    manifest_path = os.path.join(out_root_dir, manifest_file)
    with open(manifest_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filepath", "resourceType", "mrn", "encounter_id", "year"])
        for row in manifest_rows_flat:
            writer.writerow(row)

    print(f"Manifest written to {manifest_path}. Total files: {len(manifest_rows_flat)}")

    
    # smart_patients = generate_smart_patients(profiles["PATIENT"])
    # smart_dir = os.path.join(cfg.out_root_dir, "smart")
    # os.makedirs(smart_dir, exist_ok=True)

    # for p in smart_patients:
    #     # p is assumed to be a dict already; if not, adapt accordingly
    #     if isinstance(p, dict):
    #         pid = p.get("id", gen_id())
    #         p["id"] = pid
    #         path = os.path.join(smart_dir, f"{pid}_Patient.json")
    #         write_fhir(p, path)
    #     else:
    #         # if it's a model, convert to dict
    #         path = os.path.join(smart_dir, f"{getattr(p, 'id', gen_id())}_Patient.json")
    #         with open(path, "w", encoding="utf-8") as f:
    #             json.dump(p, f, default=lambda o: o.dict(), indent=2)

    if cfg.validate == 1:

        if not cfg.uscore_root or not isinstance(cfg.uscore_root, str):
            raise RuntimeError(f"Invalid uscore_root: {cfg.uscore_root}")

        if not os.path.isdir(cfg.uscore_root):
            raise RuntimeError(f"US Core profile folder not found: {cfg.uscore_root}")       

        #profiles_local = build_local_profile_paths(cfg.uscore_root)
        print(f"Loaded USCore profiles for validation from {cfg.uscore_root}")
    
        validator_jar = cfg.validator_path
        
        print("Starting validation of generated files ...")
        print(f"Loading validator jar file from: {validator_jar}")
        
        validation_results = validate_manifest(
                manifest_rows_flat,
                validator_jar=validator_jar,
                #profiles=profiles_local,
                uscore_root=cfg.uscore_root,
                out_dir=out_root_dir
            )
        print("Validation complete.")
    else:
        validation_results = []
        print("Validation skipped by default.")

    summary_json_path, summary_csv_path, summary = generate_summary(
        manifest_rows_flat, validation_results, out_root_dir
    )
    print(f"Summary written to {summary_json_path} and {summary_csv_path}")

    print("=== Summary ===")
    print(f"Total files: {summary['totals']['files']}")
    print(f"Total patients: {summary['totals']['patients']}")
    print(f"Total encounters: {summary['totals']['encounters']}")
    print(f"Validation valid: {summary['validation']['valid']}")
    print(f"Validation structural-only: {summary['validation']['valid_structural']}")
    print(f"Validation invalid: {summary['validation']['invalid']}")
    print(f"Validation errors: {summary['validation']['errors']}")
