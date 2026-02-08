## Agents

Each agent performs **one responsibility** and updates the shared state.

### Requirements Agent (`agents/requirements.py`)

**Purpose:**  
Convert a free-text clinical question into structured intent.

Example input (free text):

> “Are there any drug–drug interactions I should worry about for this ED patient in the next 12 hours?”

Structured output (stored in `state["requirements"]`):

```json
{
  "goal": "drug–drug interaction identification",
  "care_setting": "ED",
  "time_window": "next 12 hours",
  "risk_focus": "DDI"
}
```
