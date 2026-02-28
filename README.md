## Capstone_ER

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
├─ agent_system/              # LangGraph-based multi-agent orchestration
|  ├─ README.md
│  ├─ graph.py                # control flow & checkpoints
|  ├─ graph_llm.py            # LLM-based graph (test demo / future)
│  ├─ state.py                # shared, PHI-safe state schema
│  ├─ router.py               # Agent routing logic
│  ├─ agents/
│  │  ├─ README.md
│  │  ├─ requirements.py      # Clinical or operational needs → technical intent
|  |  ├─ requirements_LLM.py  # LLM-powered (test demo / future)
│  │  ├─ fhir_mapping.py      # Intent → FHIR resources & fields
│  │  ├─ smart_compile.py     # SMART scopes & launch context
│  │  ├─ scaffold.py          # repo / boilerplate generation
│  │  └─ test_agent.py        # Synthetic test generation
│  └─ tools/
│     ├─ fhir_schema_tools.py # FHIR schema helper
│     ├─ synthetic_data.py    # synthetic FHIR generators
│     └─ static_analysis.py   # Security-gate helpers
|
├─ validation/
|
├─ mcp/
|   ├─ README.md              # HAPI FHIR + WSO2 MCP Docker setup
|
├─ fhir_server/
|   ├─ README.md               # HAPI Docker setup
|   ├─ validation_pipeline/
|   |  ├─ missing_resource_analyzer.py
|   |  ├── clean_load_fhir_dataset.py
|   |  └── README.md          # dataset prep + loader to HAPI
|   └── test_queries.py
|
├─ fhir_local_loader/         # local FHIR adapter
│  ├─ config.py
│  ├─ file_scanner.py         # iterate local FHIR JSON files
│  ├─ resource_parser.py      # normalizes FHIR resources
│  ├─ index_builder.py        # build encounter-level index
│  ├─ resource_index.py       # read-only query interface
│  └─ patient_index.py        # patient-level derived index
│
├─ security_gate/             # pre-integration safety checks
│  ├─ scan_secrets.py
│  ├─ scan_logging.py
│  └─ scan_data_handling.py
│
├─ artifact_store/            # reproducible outputs
│  ├─ generated_repo/
│  └─ configs/
│
├─ trace_store/               # Audit & explainability
│  ├─ agent_decisions.jsonl
│  └─ langsmith_runs/
│
├─ notebooks/                 # sandbox for exploration & validation
│  ├─ FHIR_exploration.ipynb
|  |─ langsmith_demo.ipynb
│  └─ synthetic_case.ipynb
│
├─ .env        # API keys (ignored)
├─ .gitignore
├─ README.md
└─ docs/
    ├─ Capstone-ED_Final_Presentation.pdf
    └── FlowChart_V2_Initial_Architecture.pdf
```
#### Environment variables (`.env`)
```
OPENAI_API_KEY=sponsor_openai_key
LANGSMITH_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Capstone-ED
```

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
