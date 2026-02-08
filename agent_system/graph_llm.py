# agent_system/graph_llm.py

from langgraph.graph import StateGraph, END
from agent_system.state import AgentState
from agent_system.agents.requirements_LLM import requirements_agent_llm
from agent_system.agents.fhir_mapping import fhir_mapping_agent


def build_graph_llm():
    """
    LLM-assisted version of the baseline graph.
    """

    graph = StateGraph(AgentState)

    # nodes
    graph.add_node("requirements", requirements_agent_llm)
    graph.add_node("fhir_mapping", fhir_mapping_agent)

    # flow (implicit START)
    graph.set_entry_point("requirements")
    graph.add_edge("requirements", "fhir_mapping")
    graph.add_edge("fhir_mapping", END)

    return graph.compile()

