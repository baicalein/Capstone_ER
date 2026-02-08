from langgraph.graph import StateGraph, END
from agent_system.state import AgentState
from agent_system.agents.requirements import requirements_agent
from agent_system.agents.fhir_mapping import fhir_mapping_agent

def build_graph():
    """
    Build a linear LangGraph:
    clinical_question
        → requirements_agent
        → fhir_mapping_agent
    """
    graph = StateGraph(AgentState)

    # add nodes
    graph.add_node("requirements", requirements_agent)
    graph.add_node("fhir_mapping", fhir_mapping_agent)

    # add flow
    graph.set_entry_point("requirements")
    graph.add_edge("requirements", "fhir_mapping")
    graph.add_edge("fhir_mapping", END)

    return graph.compile()
