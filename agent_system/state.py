from typing import TypedDict, List, Optional
class AgentState(TypedDict, total=False):
    # High-level clinical intent (natural language)
    clinical_question: str
    # Structured interpretation of intent
    requirements: dict
    # FHIR resources + fields needed (schema-level only)
    fhir_mapping: dict

    # SMART scopes required
    smart_scopes: List[str]

    # Generated repo structure / files
    scaffold: dict

    # Synthetic test results
    test_results: dict

    # Compliance justification
    scope_rationale: str
