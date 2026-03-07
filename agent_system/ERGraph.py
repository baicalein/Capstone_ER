from langgraph.graph import StateGraph, END

from agent_system.ERState import ERState

from agent_system.agents.requirement_LLM2 import requirement_llm2
from agent_system.agents.validation_layer import validation_layer
from agent_system.agents.mcp_executor import mcp_executor
from agent_system.agents.aggregation import aggregation_layer
from agent_system.agents.snapshot_generator import snapshot_generator

from agent_system.error_handling.retry_policies import retry_policy


def build_er_graph(mcp_client):

    graph = StateGraph(ERState)

    # --------------------------------------------------
    # Requirement planning (LLM)
    # --------------------------------------------------

    graph.add_node("requirements", requirement_llm2)

    # --------------------------------------------------
    # Validation layer (guardrails)
    # --------------------------------------------------

    graph.add_node("validation", validation_layer)

    # --------------------------------------------------
    # MCP executor (FHIR queries)
    # --------------------------------------------------

    async def executor_node(state):
        return await mcp_executor(state, mcp_client)

    graph.add_node(
        "executor",
        executor_node,
        retry_policy=retry_policy,
    )

    # --------------------------------------------------
    # Aggregation layer
    # --------------------------------------------------

    graph.add_node("aggregation", aggregation_layer)

    # --------------------------------------------------
    # Snapshot generator (LLM)
    # --------------------------------------------------

    graph.add_node("snapshot", snapshot_generator)

    # --------------------------------------------------
    # Graph flow
    # --------------------------------------------------

    graph.set_entry_point("requirements")

    graph.add_edge("requirements", "validation")
    graph.add_edge("validation", "executor")
    graph.add_edge("executor", "aggregation")
    graph.add_edge("aggregation", "snapshot")
    graph.add_edge("snapshot", END)

    return graph.compile()