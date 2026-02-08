# fhir_loader

### Purpose

the `fhir_loader` module provides local-only abstraction layer over FHIR data.
It allows downstream agents to reason over FHIR structure and relationships without direct
interaction with raw JSON files.

This module is intentionally **read-only**, **derived**, **No network calls**

The `fhir_loader` module is responsible for:

1. Scanning local FHIR JSON resources
2. Normalizing FHIR structures
3. Building derived indexs

### File map

```text
fhir_loader/
├── config.py
│   Configuration for local paths and loader behavior
│
├── file_scanner.py
│   Iterates through local FHIR JSON files
│
├── resource_parser.py
│   Normalizes raw FHIR resources into consistent internal representations
│
├── index_builder.py
│   Builds encounter-level indexes from parsed resources
│
├── resource_index.py
│   Read-only query interface over encounter-derived data
│
├── patient_index.py
│   Patient-level derived index built on top of encounter indexes
```
### Indexing

#### Encounter-level Index
FHIR resources are grouped and indexed by encounter.
#### ResourceIndex
Provides read-only query access for agents, such as:
- Resource counts
- Resource types per encounter
#### PatientIndex
Derives patient-to-encounter relationships and supports:
- Listing all encounters for a patient
- Identifying the most recent encounter

### Intended Usage
Agents does not read raw FHIR JSON directly.

This module is designed to be consumed by:
- LangGraph-based agents
- FHIR schema-mapping agents
- SMART-on-FHIR compilation and validation logic
- Synthetic testing and design validation workflows

