from agent_system.state import AgentState

def requirements_agent(state: AgentState) -> AgentState:
    clinical_question = state.get("clinical_question", "")

    # Placeholder
    requirements = {
    "goal": "drug–drug interaction identification",
    "care_setting": "ED",
    "time_window": "next 12 hours",
    "risk_focus": "DDI",
    }

    return {
        **state,
        "requirements": requirements,
    }
