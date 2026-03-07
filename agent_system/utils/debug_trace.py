from typing import Dict, Any
import json


def debug_trace(node_name: str, state: Dict[str, Any]) -> None:
    """
    Print a readable snapshot of the state
    when entering a LangGraph node.
    """

    print("\n")
    print("=" * 60)
    print(f"NODE: {node_name}")
    print("=" * 60)

    try:
        print(json.dumps(state, indent=2, default=str))
    except Exception:
        print(state)

    print("=" * 60)
