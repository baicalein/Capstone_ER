## agent_system

This folder contains the LangGraph-based multi-agent orchestration layer for the roject.

The agent system is responsible for translating clinical or operational intent into structured, verifiable artifacts (FHIR mappings, SMART scopes, scaffolds, tests), without directly accessing raw FHIR data or live systems. Agents operate on *derived structure* and *schemas*, not patient data. Agents do not read raw FHIR JSON, or make network calls.


### Design principles

- **Orchestration, not execution**
- **PHI-safe by construction**
- **Deterministic control flow**
- **Explicit agent responsibilities**
- **Auditable decisions**

###  Core components

#### control layer

- `graph.py`  
  Defines the LangGraph execution graph and checkpoints.

- `router.py`  
  Routes state between agents based on intent and intermediate results.

- `state.py`  
  Defines the shared state schema passed between agents.

#### Agents

Each agent has a single responsibility:

- `requirements.py`  
  Converts clinical or operational needs into structured technical intent.

- `fhir_mapping.py`  
  Maps intent to FHIR resource types and fields.

- `smart_compile.py`  
  validates and compiles SMART-on-FHIR scopes and launch context.

- `scaffold.py`  
  Generates repository structure and boilerplate (no execution).

- `test_agent.py`  
  Produces synthetic tests using mock FHIR payloads.

#### Tools

Shared utilities used by agents:

- `fhir_schema_tools.py`  
  Helpers for working with FHIR definitions and profiles.

- `synthetic_data.py`  
  Generates synthetic FHIR resources for testing and validation.

- `static_analysis.py`  
  Security-gate helpers used to detect unsafe patterns.
### LLM-based Experimental Components

We added an experimental LLM-based variant of the requirements agent for testing and future extension:

- `agent_system/agents/requirements_LLM.py`
LLM-powered version of the requirements agent using GPT-5 mini (max tokens: 3000).
This is for prototyping and comparison with the rule-based agent.

- `agent_system/graph_llm.py`
LangGraph that uses the LLM-based requirements agent instead of the rule-based one.
This graph is intended for demos, experimentation, and future development.
### Relationship to other modules

- Consumes **derived indexes** from `fhir_loader/`(currently encouter/patient indexes)
- Produces outputs in `artifact_store/`
- Writes decision traces to `trace_store/`
- Must pass checks in `security_gate/` before integration
