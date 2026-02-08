from agent_system.state import AgentState

def requirements_agent(state: AgentState) -> AgentState:
    clinical_question = state.get("clinical_question", "")

    #placeholder
    requirements = {
    "goal": "drug safety", #high level clinical objective
    "care_setting": "ED",
    "time_window": "next 12 hours",
    "risk_focus": "drug allergy",#specific focus
    }

    return {
        **state,
        "requirements": requirements,
    }
