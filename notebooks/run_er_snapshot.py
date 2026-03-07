from dotenv import load_dotenv
load_dotenv()
import re
import asyncio

from mcp_client.mcp_client import MCPClient
from agent_system.ERGraph import build_er_graph
from langsmith import traceable


# --------------------------------------------------
# Extract patient_id from sentence
# --------------------------------------------------

def extract_patient_id(text: str):

    match = re.search(r"patient-[A-Za-z0-9]+", text)

    if match:
        return match.group(0)

    return None


# --------------------------------------------------
# Main
# --------------------------------------------------
@traceable(name="ER Snapshot Run")
def main():

    mcp_client = MCPClient(
        url="http://localhost:8000/mcp"
    )

    graph = build_er_graph(mcp_client)

    # -----------------------------
    # User input
    # -----------------------------

    user_input = input("\nEnter your request:\n> ")

    patient_id = extract_patient_id(user_input)

    if not patient_id:
        print("\n❌ Could not find patient_id in the sentence.")
        print("Example: Show me ER snapshot for patient-0L725\n")
        return

    # -----------------------------
    # Build state
    # -----------------------------

    state = {
        "user_input": user_input,
        "patient_id": patient_id,
        "use_case": "er_snapshot",
    }

    # -----------------------------
    # Run graph
    # -----------------------------

    result = asyncio.run(
        graph.ainvoke(state)
    )

    print("\n==============================")
    print("ER SNAPSHOT")
    print("==============================\n")

    print(result["snapshot"])


if __name__ == "__main__":
    main()