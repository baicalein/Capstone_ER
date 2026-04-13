# Capstone_ER

![Python](https://img.shields.io/badge/python-3.10+-blue)
![LangGraph](https://img.shields.io/badge/orchestration-LangGraph-purple)
![FHIR](https://img.shields.io/badge/standard-FHIR-orange)
![Workspace](https://img.shields.io/badge/workspace-A%20(No%20PHI)-brightgreen)
![Data](https://img.shields.io/badge/data-synthetic%20FHIR-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-yellow)


Capstone_ER is a SMART-on-FHIR app factory prototype built with **LangGraph** to support the design, validation, and secure scaffolding of Epic-compatible SMART applications.

This repository focuses on **Workspace A (No PHI)**: deterministic orchestration, FHIR-aware tooling, synthetic testing, and security-first design before any sandbox or production integration.

This implementation follows a **workspace-based escalation model**:

#### Workspace A — Design & Scaffolding
- No Protected Health Information (PHI)
- Synthetic FHIR bundles only
- Deterministic LangGraph orchestration
- SMART scope compilation
- Test and security artifact generation

Future work (not included in this repository):
- **Workspace B**: Epic sandbox integration
- **Workspace C**: Secure PHI enclave (break-glass only)

## Goals

This project demonstrates how a SMART-on-FHIR application can be:

- Designed **deterministically**
- Built with **least-privilege SMART scopes**
- Audited through **reproducible artifacts**
- Governed through **explicit workspace boundaries**

The focus is on **orchestration, safe data boundaries, and reproducibility**, aligned with Epic SMART-on-FHIR constraints.

## Repository structure

```text
Capstone-ER/
├─ agent_system/               # LangGraph-based multi-agent orchestration
│  ├─ README.md                # How to run agent system
│  ├─ ARCHITECTURE_OVERVIEW.md  # ER snapshot agent workflow + logic
│  ├─ graph.py                 # Control flow & checkpoints
│  ├─ graph_llm.py             # LLM-based graph (test demo)
│  ├─ ERGraph.py               # LLM-based graph (for ER snapshot use-case)
│  ├─ state.py                 # Shared, PHI-safe state schema
│  ├─ ERstate.py               # State for ER snapshot use-case
│  ├─ router.py                # Multi-agent routing logic
│  ├─ agents/                  # Node implementations
│  │  ├─ README.md
│  │  ├─ requirements.py       # Clinical or operational needs to technical intent
│  │  ├─ requirements_LLM.py   # LLM extracts patient_id + use_case (demo)
│  │  ├─ requirements_LLM2.py  # LLM extracts patient_id for ER snapshot
│  │  ├─ validation_layer.py    # Policy enforcement & interrupt()
│  │  ├─ mcp_executor.py       # Call MCP + ER encounter filtering logic
│  │  ├─ aggregation.py        # Combine patient + ER + Meds + Allergies
│  │  ├─ snapshot_generator.py  # LLM-based ER summary formatting
│  │  └─ fhir_mapping.py       # Intent to FHIR resources & fields (demo)
│  ├─ error_handling/          # Reliability layer
│  │  ├─ retry_policies.py     # RetryPolicy configs (MCP only)
│  │  └─ error_types.py        # Custom ToolError/Validation error 
│  └─ utils/
│     └─ debug_trace.py        # Local trace utility (replaces LangSmith)
|
├─ mcp_client/                 # Renamed from /mcp to avoid package conflict
│  ├─ README.md                # HAPI FHIR + WSO2 MCP Docker setup
│  └─ mcp_client.py            # Local wrapper around MCP tools
|
├─ fhir_server/                # FHIR environment management
│  ├─ README.md                # HAPI Docker setup
│  ├─ validation_pipeline/
│  │  ├─ missing_resource_analyzer.py
│  │  ├─ clean_load_fhir_dataset.py
│  │  └─ README.md             # Dataset prep + loader to HAPI
│  └─ test_queries.py
|
├─ audit/                      # Trace store for compliance
│  ├─ README.md                
│  ├─ audit_logger.py          # Idempotent log_event()
│  ├─ decorator.py             # @audited_node decorator
│  ├─ trace_writer.py          # Execution traces (per run id)
│  ├─ schemas.py               # Structured audit event schemas
│  └─ trace_store.jsonl        # Local execution logs
|
├─ fhir_local_loader/          # Local FHIR adapter
│  ├─ config.py
│  ├─ file_scanner.py          # Iterate local FHIR JSON files
│  ├─ resource_parser.py       # Normalizes FHIR resources
│  ├─ index_builder.py         # Build encounter-level index
│  ├─ resource_index.py        # Read-only query interface
│  └─ patient_index.py         # Patient-level derived index
│
├─ security_gate/              # Pre-integration safety checks
│  ├─ scan_secrets.py
│  ├─ scan_logging.py
│  └─ scan_data_handling.py
│
├─ artifact_store/             # Reproducible outputs
│  ├─ generated_repo/
│  └─ configs/
│
├─ notebooks/                  # Sandbox for exploration & validation
│  ├─ FHIR_exploration.ipynb
│  ├─ langsmith_demo.ipynb     # Test demo
│  ├─ run_er_snapshot.py       # Entry point: run from project root
│  └─ synthetic_case.ipynb
│
├─ FHIR Synthetic Data/        # Data generation tools
│  ├─ src/uscore_synth/
│  │  ├─ __init__.py
│  │  ├─ cli.py
│  │  ├─ config.py
│  │  └─ generator.py
│  ├─ pyproject.toml
│  ├─ set_java_path.ps1
│  └─ README.md
│
├─ .env                        # API keys (ignored)
├─ .gitignore
├─ README.md
└─ docs/
   ├─ Capstone-ED_Final_Presentation.pdf
   └─ FlowChart_V2_Initial_Architecture.pdf
```
#### Environment variables (`.env`)
```
OPENAI_API_KEY=sponsor_openai_key
LANGSMITH_API_KEY=sponsor_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Capstone_ER
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
FHIR_DATA_ROOT= (Optional)
TRACE_FILE = [path to trace_store.jsonl] (example: /Capstone_ER/audit/trace_store.jsonl)
```
## Architecture

The system follows a deterministic pipeline to transform clinical intent into a structured medical snapshot. For a detailed system design, see the following: [Architecture Overview](agent_system/ARCHITECTURE_OVERVIEW.md).

## Technologies used

- Python
- LangGraph (deterministic multi-agent orchestration)
- SMART-on-FHIR / HL7 FHIR
- Synthetic FHIR data
- Epic SMART design constraints
- Security-first design

## Disclaimer

This repository is for academic and research purposes only. 
It doesn't connect to live Epic systems and does not process PHI.
