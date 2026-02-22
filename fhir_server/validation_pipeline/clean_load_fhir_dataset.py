import os
import json
import argparse
import requests
from pathlib import Path
from collections import defaultdict


# Dependency-aware load order
RESOURCE_ORDER = [
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
    "DocumentReference"
]


def normalize_id(value: str) -> str:
    """Normalize FHIR ID by replacing underscores with dashes."""
    return value.replace("_", "-")


def normalize_references(obj):
    """Recursively normalize reference IDs inside a FHIR resource."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key == "reference" and isinstance(val, str):
                parts = val.split("/")
                if len(parts) == 2:
                    resource_type, rid = parts
                    obj[key] = f"{resource_type}/{normalize_id(rid)}"
            else:
                normalize_references(val)
    elif isinstance(obj, list):
        for item in obj:
            normalize_references(item)


def load_resources(data_folder: Path, server_url: str, fail_fast: bool = False):
    resources_by_type = defaultdict(list)

    json_files = list(data_folder.glob("*.json"))
    if not json_files:
        raise ValueError("No JSON files found in provided dataset folder.")

    print(f"\nReading {len(json_files)} JSON files...")

    # Group resources by type
    for file in json_files:
        try:
            with open(file, "r") as f:
                data = json.load(f)
                rtype = data.get("resourceType")
                if rtype:
                    resources_by_type[rtype].append(data)
        except Exception as e:
            print(f"Failed reading {file.name}: {e}")

    print("\nStarting resource upload...\n")

    total_loaded = 0
    total_failed = 0

    for rtype in RESOURCE_ORDER:
        if rtype not in resources_by_type:
            continue

        print(f"Uploading {rtype} resources...")

        success_count = 0

        for resource in resources_by_type[rtype]:
            if "id" not in resource:
                continue

            original_id = resource["id"]
            normalized_id = normalize_id(original_id)
            resource["id"] = normalized_id

            normalize_references(resource)

            url = f"{server_url.rstrip('/')}/{rtype}/{normalized_id}"

            response = requests.put(
                url,
                headers={"Content-Type": "application/fhir+json"},
                json=resource
            )

            if response.status_code not in (200, 201):
                total_failed += 1
                print(f"  ✗ Failed: {rtype}/{normalized_id}")
                if fail_fast:
                    raise RuntimeError(response.text)
            else:
                success_count += 1
                total_loaded += 1

        print(f"  ✓ {success_count} {rtype} resources uploaded.\n")

    print("-" * 50)
    print(f"Upload complete.")
    print(f"Total Loaded: {total_loaded}")
    print(f"Total Failed: {total_failed}")
    print("-" * 50)


# -----------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load cleaned FHIR dataset into a HAPI FHIR server."
    )

    parser.add_argument(
        "--data-folder",
        required=True,
        help="Path to folder containing FHIR JSON files"
    )

    parser.add_argument(
        "--server-url",
        default="http://localhost:8080/fhir",
        help="FHIR server base URL (default: http://localhost:8080/fhir)"
    )

    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop execution immediately if a resource fails to upload"
    )

    args = parser.parse_args()

    load_resources(
        data_folder=Path(args.data_folder),
        server_url=args.server_url,
        fail_fast=args.fail_fast
    )