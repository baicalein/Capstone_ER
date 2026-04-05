# FHIR Dataset Validation & HAPI Load Pipeline

This module documents the full validation, correction, and ingestion process used to prepare the synthetic FHIR dataset for the HAPI server.

## Environment & Pathing Requirements

**Crucial:** To resolve environment-specific pathing errors, ensure that your primary execution script (`run_er_snapshot.py`) is moved to the **root directory** of the project rather than being run from within sub-folders or the `notebooks` directory.

### OS-Specific Setup
If you need to initialize a local environment file for server credentials in this directory:
* **Windows (PowerShell):** `new-item .env`
* **macOS/Linux:** `touch .env`
  
## Initial Discovery

During initial upload attempts to HAPI FHIR, server validation errors indicated unresolved references. Exploratory analysis identified that:

- Practitioner resources were referenced but not present (429 IDs)
- Location resources were referenced but not present
- Broken references caused upload failures

The validation script ensures referential integrity, valid FHIR-compliant IDs, and dependency-aware uploads.

Before integrating MCP tools with a FHIR server, the dataset must:

- Maintain referential integrity
- Contain all referenced Location and Practitioner resources
- Use valid FHIR-compliant resource IDs
- Upload successfully to a HAPI FHIR server

This module implements:

1. Dataset validation
2. Missing resource detection
3. Stub resource generation
4. Dependency-aware upload into HAPI FHIR


## Files

| File | Purpose |
|------|---------|
| `missing_resource_analyzer.py` | Detect missing Location/Practitioner references and optionally generate stub resources |
| `clean_load_fhir_dataset.py` | Normalize IDs and upload dataset to HAPI FHIR in dependency order |


## Step 1. Analyze Dataset

Detect missing Location and Practitioner references:

**Note on Command Formatting:** When executing the following commands, ensure the entire string is entered as a **single continuous line** in your terminal to prevent shell parsing errors.

```bash
python missing_resource_analyzer.py --data-folder <PATH_TO_FHIR_FOLDER>
```

Example:

```bash
python missing_resource_analyzer.py --data-folder ../Forge-N-FHIR/synthetic-ivy-hip-emr/FHIR
```


## Optional: Export Tableau Datasets

```bash
python missing_resource_analyzer.py --data-folder ../Forge-N-FHIR/synthetic-ivy-hip-emr/FHIR --export-tableau
```

This produces CSV files for visual analysis.


## Generate Missing Resources

This creates minimal valid JSON resources for missing Location and Practitioner entries in the minimal_resources/ directory.

```bash
python missing_resource_analyzer.py --data-folder ../Forge-N-FHIR/synthetic-ivy-hip-emr/FHIR --generate-stubs
```

If stub generation is used, manually copy the generated JSON files from minimal_resources/ into your FHIR dataset folder before running the loader.

## Step 2. Load Dataset into HAPI FHIR

Upload dataset:

```bash
python clean_load_fhir_dataset.py --data-folder <PATH_TO_UPDATED_FHIR_FOLDER>
```

Example:

```bash
python clean_load_fhir_dataset.py --data-folder ../Forge-N-FHIR/synthetic-ivy-hip-emr/FHIR
```


## Optional Parameters

* Custom FHIR server: --server-url http://localhost:8080/fhir
* Stop immediately on failure: --fail-fast

## Flow

**Validation → Stub Generation → ID Normalization → Dependency-Ordered Upload → MCP Integration**

## Final Dataset

The final cleaned dataset version is used by all team members for MCP testing to ensure a consistent environment state across the project.
