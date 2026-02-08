# agent_system

This directory contains the LangGraph-based multi-agent orchestration layer for the Capstone-ER project.

The agent system is responsible for translating clinical or operational intent into structured, verifiable artifacts (FHIR mappings, SMART scopes, scaffolds, and tests), without directly accessing raw FHIR data or live systems.


## Design Principles

- **Orchestration, not execution**
- **PHI-safe by construction**
- **Deterministic control flow**
- **Explicit agent responsibilities**
- **Auditable decisions**

Agents operate on *derived structure* and *schemas*, not patient data.


## Core Components

### Control Layer

- `graph.py`  
  Defines the LangGraph execution graph and checkpoints.

- `router.py`  
  Routes state between agents based on intent and intermediate results.

- `state.py`  
  Defines the shared, PHI-safe state schema passed between agents.

### Agents

Each agent has a single, narrow responsibility:

- `requirements.py`  
  Converts clinical or operational needs into structured technical intent.

- `fhir_mapping.py`  
  Maps intent to FHIR resource types and fields (schema-level only).

- `smart_compile.py`  
  Validates and compiles SMART-on-FHIR scopes and launch context.

- `scaffold.py`  
  Generates repository structure and boilerplate (no execution).

- `test_agent.py`  
  Produces synthetic tests using mock FHIR payloads.

Agents **must not**:
- Read raw FHIR JSON
- Make network calls
- Persist PHI

### Tools

Shared utilities used by agents:

- `fhir_schema_tools.py`  
  Helpers for working with FHIR definitions and profiles.

- `synthetic_data.py`  
  Generates synthetic FHIR resources for testing and validation.

- `static_analysis.py`  
  Security-gate helpers used to detect unsafe patterns.

## Relationship to Other Modules

- Consumes **derived indexes** from `fhir_loader/`
- Produces outputs in `artifact_store/`
- Writes decision traces to `trace_store/`
- Must pass checks in `security_gate/` before integration

## Scope and Status

**Current scope**
- Multi-agent control flow
- Schema-level reasoning
- Synthetic and local validation

**Out of scope**
- Live SMART-on-FHIR execution
- Runtime clinical inference
- Direct EHR or FHIR server access
