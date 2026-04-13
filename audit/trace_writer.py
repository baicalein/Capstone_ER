
import os
import json
from dotenv import load_dotenv

load_dotenv()

trace_file_path = os.getenv("TRACE_FILE", "trace_store.jsonl")


def write_trace(event: dict):
    """
    Appends a single event to the trace file in JSONL format.
    """

    if not isinstance(event, dict):
        raise TypeError(f"Expected dict, got {type(event)}")

    with open(trace_file_path, "a") as f:
        f.write(json.dumps(event) + "\n")