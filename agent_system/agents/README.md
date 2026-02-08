## Agents

Each agent performs **one responsibility** and updates the shared state.

### Requirements Agent (`agents/requirements.py`)

**Purpose:**  
Convert a free-text clinical question into structured intent. This agent does not query FHIR data, and keys may expand as the project evolves.

Example input (free text):

> “Does this ED patient have any drug allergies I should be concerned about in the next 12 hours?”

Structured output (stored in `state["requirements"]`):

```json
{
  "goal": "drug safety",
  "care_setting": "ED",
  "time_window": "next 12 hours",
  "risk_focus": "drug allergy"
}
```
### FHIR Mapping Agent (`agents/fhir_mapping.py`)

**Purpose:**  
convert structured clinical requirements into a schema-level list of required FHIR resources and fields.

This agent answers the question:

> “Which FHIR data types are needed to assess this clinical risk?”

Example: Drug Allergy Risk: if
```json
"risk_focus": "drug allergy"
```
The agent maps to the following FHIR resources:
- AllergyIntolerance
- MedicationRequest
- Encounter
