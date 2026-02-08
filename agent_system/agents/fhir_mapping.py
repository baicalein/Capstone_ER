from agent_system.state import AgentState

def fhir_mapping_agent(state: AgentState) -> AgentState:
    """
    Translate structured clinical requirements into
    schema-level FHIR resource + field requirements
    """
    requirements = state.get("requirements", {})
    risk_focus = requirements.get("risk_focus", "").lower()
    fhir_mapping = {}

    if risk_focus == "drug allergy":
        fhir_mapping = {
            "AllergyIntolerance": [
                "clinicalStatus",
                "verificationStatus",
                "code",            # substance (e.g. penicillin)
                "reaction",        # reaction detail
                "criticality",
            ],
            "MedicationRequest": [
                "medicationCodeableConcept",
                "authoredOn",
                "status",
            ],
            "Encounter": [
                "period.start",
                "class",
            ],
        }

    
    return {
        **state,
        "fhir_mapping": fhir_mapping,
    }
