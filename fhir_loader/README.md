# fhir_loader

## Purpose

The `fhir_loader` module provides a **PHI-safe, local-only abstraction layer** over FHIR data.
It allows downstream agents to reason over **FHIR structure and relationships** without direct
interaction with raw JSON files or live FHIR endpoints.

This module is intentionally **read-only**, **derived**, and **network-isolated**.


## Design Rationale

Key design principles:

- **No network calls**  
  All data is loaded from local FHIR JSON files only.

- **No PHI persistence beyond runtime**  
  No databases, caches, or serialized artifacts containing PHI.

- **Read-only, derived indexes**  
  All indexes are computed in memory and exposed through query-only APIs.

- **Explicit guarantees**  
  Structural assumptions are documented (e.g., `encounter_id` may be `None`).

This allows agents to reason about **FHIR schema and linkage**, not patient-identifiable data.

## Responsibilities

The `fhir_loader` module is responsible for:

1. Scanning local FHIR JSON resources
2. Normalizing heterogeneous FHIR structures
3. Building derived, queryable indexes
4. Exposing safe interfaces for higher-level agents

This module does **not**:

- Call live FHIR servers
- Persist patient data
- Perform clinical decision-making
- Mutate source resources

## File Overview

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
## Indexing Model

### Encounter-level Index
FHIR resources are grouped and indexed by encounter.

### ResourceIndex
Provides read-only query access for agents, such as:
- Resource counts
- Resource types per encounter

### PatientIndex
Derives patient-to-encounter relationships and supports:
- Listing all encounters for a patient
- Identifying the most recent encounter

All indexes are **derived**, **immutable**, and **in-memory only**.


## Intended Usage

This module is designed to be consumed by:
- LangGraph-based agents
- FHIR schema-mapping agents
- SMART-on-FHIR compilation and validation logic
- Synthetic testing and design validation workflows

Agents **must not** read raw FHIR JSON directly.


## Security Notes

- Local-only execution
- No credentials, tokens, or endpoints
- No PHI persistence
- Generated files and `__pycache__/` are excluded from version control


## Status

### Current Scope
- Structural indexing
- Patient–encounter relationships
- Synthetic and local test data support

### Out of Scope (Future Work)
- Live SMART-on-FHIR integration
- Server-backed persistence
- Clinical inference logic
