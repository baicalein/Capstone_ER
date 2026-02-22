import requests
from typing import List, Dict, Optional

BASE_URL = "http://localhost:8080/fhir"



# Core HTTP Utilities


def fetch_all_pages(url: str) -> List[Dict]:
    """
    Retrieve all resources across paginated FHIR search results.
    """
    resources = []

    while url:
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Request failed: {url} ({response.status_code})")
            return resources

        bundle = response.json()

        entries = bundle.get("entry", [])
        for entry in entries:
            resources.append(entry["resource"])

        # Follow pagination
        next_link = None
        for link in bundle.get("link", []):
            if link.get("relation") == "next":
                next_link = link.get("url")

        url = next_link

    return resources


def get_summary_count(resource_type: str) -> int:
    response = requests.get(f"{BASE_URL}/{resource_type}?_summary=count")
    if response.status_code != 200:
        return 0
    return response.json().get("total", 0)



# Basic Server Checks

def check_server():
    print("\n=== Checking HAPI FHIR Server ===")
    r = requests.get(f"{BASE_URL}/metadata")
    if r.status_code == 200:
        print(" Server is running.")
    else:
        print("Server not reachable.")


def count_resources(resource_type: str):
    print(f"\n=== Counting {resource_type} ===")
    total = get_summary_count(resource_type)
    print(f"Total {resource_type}: {total}")


# ER only


def detect_er_location() -> Optional[str]:
    print("\n=== Detecting ER Location ===")

    locations = fetch_all_pages(f"{BASE_URL}/Location")

    for location in locations:
        name = location.get("name", "").lower()
        if "er" in name or "emergency" in name:
            er_id = location.get("id")
            print(f"✓ ER Location detected: Location/{er_id}")
            return er_id

    print("No ER location detected.")
    return None



# ER-Based Queries (Pagination Safe)


def get_er_encounters(er_id: str) -> List[Dict]:
    print("\n=== Retrieving ER Encounters (all pages) ===")

    encounters = fetch_all_pages(
        f"{BASE_URL}/Encounter?location=Location/{er_id}"
    )

    print(f"ER Encounters found: {len(encounters)}")
    return encounters


def count_unique_er_patients(encounters: List[Dict]):
    print("\n=== Counting Unique ER Patients ===")

    patient_refs = set()

    for encounter in encounters:
        subject = encounter.get("subject", {})
        ref = subject.get("reference")
        if ref:
            patient_refs.add(ref)

    print(f"✓ Unique ER Patients: {len(patient_refs)}")

# Main Execution

if __name__ == "__main__":

    
    print("FHIR SERVER SANITY CHECK")
    

    check_server()

    # Global counts
    count_resources("Patient")
    count_resources("Encounter")
    count_resources("Observation")
    count_resources("Location")

    # ER-specific checks
    er_id = detect_er_location()

    if er_id:
        er_encounters = get_er_encounters(er_id)

        if er_encounters:
            count_unique_er_patients(er_encounters)
            
    print("test done")
    