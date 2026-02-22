import json
import argparse
from pathlib import Path
from collections import defaultdict
import pandas as pd


class MissingResourceAnalyzer:
    """
    Analyze a FHIR dataset to identify missing Location and Practitioner references,
    optionally export analysis datasets, and optionally generate minimal stub resources.
    """

    def __init__(self, data_folder: Path):
        self.data_folder = Path(data_folder)
        self.references = []
        self.existing_resources = set()
        self.missing_refs = defaultdict(set)

    # -----------------------------------------------------
    # Core Reference Extraction
    # -----------------------------------------------------

    def extract_references(self, obj, source_resource, path=""):
        refs = []

        if isinstance(obj, dict):
            if "reference" in obj:
                ref_value = obj["reference"]
                if "/" in ref_value:
                    target_type, target_id = ref_value.split("/", 1)

                    refs.append({
                        "source_type": source_resource.get("resourceType"),
                        "source_id": source_resource.get("id"),
                        "target_type": target_type,
                        "target_id": target_id,
                        "field_path": path,
                        "reference_string": ref_value,
                        "exists": False
                    })

            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                refs.extend(self.extract_references(value, source_resource, new_path))

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                refs.extend(self.extract_references(item, source_resource, new_path))

        return refs

    # -----------------------------------------------------
    # Dataset Processing
    # -----------------------------------------------------

    def load_json(self, filepath: Path):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def record_existing_resource(self, resource):
        rtype = resource.get("resourceType")
        rid = resource.get("id")
        if rtype and rid:
            self.existing_resources.add(f"{rtype}/{rid}")

    def process_resource(self, resource):
        if not resource:
            return

        rtype = resource.get("resourceType")
        rid = resource.get("id")
        if not rtype or not rid:
            return

        refs = self.extract_references(resource, resource)

        for ref in refs:
            key = f"{ref['target_type']}/{ref['target_id']}"
            ref["exists"] = key in self.existing_resources

            if not ref["exists"]:
                self.missing_refs[ref["target_type"]].add(ref["target_id"])

        self.references.extend(refs)

    def analyze(self):
        json_files = list(self.data_folder.glob("*.json"))

        if not json_files:
            raise ValueError("No JSON files found in provided dataset folder.")

        # Pass 1: record existing resources
        for file in json_files:
            data = self.load_json(file)
            if not data:
                continue

            if data.get("resourceType") == "Bundle":
                for entry in data.get("entry", []):
                    self.record_existing_resource(entry.get("resource", {}))
            else:
                self.record_existing_resource(data)

        # Pass 2: extract references
        for file in json_files:
            data = self.load_json(file)
            if not data:
                continue

            if data.get("resourceType") == "Bundle":
                for entry in data.get("entry", []):
                    self.process_resource(entry.get("resource", {}))
            else:
                self.process_resource(data)

    # -----------------------------------------------------
    # Reporting
    # -----------------------------------------------------

    def summary_dataframe(self):
        df = pd.DataFrame(self.references)

        if df.empty:
            return pd.DataFrame()

        df["status"] = df["exists"].map({True: "EXISTS", False: "MISSING"})

        summary = df[df["target_type"].isin(["Location", "Practitioner"])]

        return summary

    def missing_summary(self):
        summary = []

        for rtype in ["Location", "Practitioner"]:
            refs = [r for r in self.references if r["target_type"] == rtype]
            total_refs = len(refs)
            missing_refs = len([r for r in refs if not r["exists"]])
            unique_missing = len(self.missing_refs.get(rtype, set()))

            summary.append({
                "ResourceType": rtype,
                "TotalReferences": total_refs,
                "MissingReferences": missing_refs,
                "UniqueMissingIDs": unique_missing
            })

        return pd.DataFrame(summary)

    def print_report(self):
        print("\nFHIR Missing Resource Analysis")
        print("-" * 40)

        summary = self.missing_summary()
        print(summary.to_string(index=False))

    # -----------------------------------------------------
    # Optional Exports
    # -----------------------------------------------------

    def export_tableau(self, output_folder="analysis_exports"):
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)

        detail_df = self.summary_dataframe()
        if not detail_df.empty:
            detail_df.to_csv(output_path / "location_practitioner_references.csv", index=False)

        summary_df = self.missing_summary()
        summary_df.to_csv(output_path / "missing_resources_summary.csv", index=False)

        return output_path

    # -----------------------------------------------------
    # Stub Generation
    # -----------------------------------------------------

    def generate_minimal_resources(self, output_folder="minimal_resources"):
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)

        # Location stubs
        for loc_id in sorted(self.missing_refs.get("Location", [])):
            location = {
                "resourceType": "Location",
                "id": loc_id,
                "status": "active",
                "mode": "instance",
                "name": f"Location {loc_id}"
            }

            with open(output_path / f"Location_{loc_id}.json", "w") as f:
                json.dump(location, f, indent=2)

        # Practitioner stubs
        for prac_id in sorted(self.missing_refs.get("Practitioner", [])):
            practitioner = {
                "resourceType": "Practitioner",
                "id": prac_id,
                "active": True,
                "name": [{
                    "text": f"Provider {prac_id}"
                }]
            }

            with open(output_path / f"Practitioner_{prac_id}.json", "w") as f:
                json.dump(practitioner, f, indent=2)

        return output_path


# -----------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze FHIR dataset for missing Location and Practitioner resources."
    )
    parser.add_argument(
        "--data-folder",
        required=True,
        help="Path to folder containing FHIR JSON files"
    )
    parser.add_argument(
        "--export-tableau",
        action="store_true",
        help="Export CSV files for Tableau analysis"
    )
    parser.add_argument(
        "--generate-stubs",
        action="store_true",
        help="Generate minimal missing Location/Practitioner JSON resources"
    )

    args = parser.parse_args()

    analyzer = MissingResourceAnalyzer(Path(args.data_folder))
    analyzer.analyze()
    analyzer.print_report()

    if args.export_tableau:
        analyzer.export_tableau()

    if args.generate_stubs:
        analyzer.generate_minimal_resources()