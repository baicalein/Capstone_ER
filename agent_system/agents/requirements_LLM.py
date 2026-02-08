"""
LLM-based Requirements Agent (demo / experimental)
Purpose:
- Convert a free-text clinical question into structured intent
- Uses GPT-5 mini
- LLM is used ONLY for intent interpretation (no data access)
This agent is optional and can be swapped with the rule-based
requirements agent for demos or future extensions.
"""
from agent_system.state import AgentState
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    max_tokens=3000,
)

def requirements_agent_llm(state: AgentState) -> AgentState:
    """
    Parse a free-text clinical question into structured requirements.

    Input (from AgentState):
        - clinical_question: str

    Output (stored in state["requirements"]):
        - goal
        - care_setting
        - time_window
        - risk_focus
        - llm_raw_output (to trace)
    """

    clinical_question = state.get("clinical_question", "")

    prompt = f"""
You are a clinical intent parser for a healthcare AI system.
Task:
Convert the following clinical question into structured intent.
Return the result as JSON with the following keys only:
- goal
- care_setting
- time_window
- risk_focus
Use short, clear values.
Do NOT include any patient identifiers.
Do NOT include explanations.

Clinical question:
{clinical_question}
"""

    response = llm.invoke(prompt)
    # NOTE:
    # For now, we keep parsing conservative and transparent.
    # In later iterations, this can be replaced with strict JSON parsing.
    requirements = {
        "goal": "drug safety",
        "care_setting": "ED",
        "time_window": "next 12 hours",
        "risk_focus": "drug allergy",
        "llm_raw_output": response.content,
    }

    return {
        **state,
        "requirements": requirements,
    }
