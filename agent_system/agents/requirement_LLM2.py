import json
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI

from agent_system.utils.debug_trace import debug_trace


# --------------------------------------------------
# Initialize LLM
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    max_tokens=2000,
)


# --------------------------------------------------
# Dataset schema awareness
# --------------------------------------------------

AVAILABLE_RESOURCES = [
    "Location",
    "Practitioner",
    "Patient",
    "EpisodeOfCare",
    "Encounter",
    "AllergyIntolerance",
    "Goal",
    "Immunization",
    "Procedure",
    "MedicationRequest",
    "FamilyMemberHistory",
    "Observation",
    "ImagingStudy",
    "DiagnosticReport",
    "DocumentReference",
]


# --------------------------------------------------
# Preferred resources for ER snapshot
# --------------------------------------------------

PREFERRED_RESOURCES = [
    "Patient",
    "Encounter",
    "MedicationRequest",
    "AllergyIntolerance",
]


# --------------------------------------------------
# FHIR dependency knowledge
# --------------------------------------------------

FHIR_DEPENDENCIES = {

    "Encounter": ["Patient"],

    "Observation": ["Encounter", "Patient"],

    "DiagnosticReport": ["Encounter", "Patient"],

    "Procedure": ["Encounter", "Patient"],

    "MedicationRequest": ["Patient"],

    "AllergyIntolerance": ["Patient"],

    "ImagingStudy": ["Encounter"],

    "DocumentReference": ["Patient"],

    "FamilyMemberHistory": ["Patient"],

    "EpisodeOfCare": ["Patient"],

    "Goal": ["Patient"],

    "Immunization": ["Patient"],
}


# --------------------------------------------------
# Dependency expansion
# --------------------------------------------------

def expand_dependencies(resources: List[str]) -> List[str]:

    expanded = set(resources)

    changed = True

    while changed:

        changed = False

        for r in list(expanded):

            deps = FHIR_DEPENDENCIES.get(r, [])

            for d in deps:

                if d not in expanded:
                    expanded.add(d)
                    changed = True

    return list(expanded)


# --------------------------------------------------
# Requirement LLM Node
# --------------------------------------------------

def requirement_llm2(state: Dict[str, Any]) -> Dict[str, Any]:

    debug_trace("requirement_llm2 (input)", state)

    question = state.get("question", "")
    patient_id = state.get("patient_id")

    prompt = f"""
You are a clinical data planner for a hospital AI system.

The dataset contains these FHIR resources:

{AVAILABLE_RESOURCES}

However, the dataset is synthetic and some resources
(such as Observation) have limited clinical richness.

For ER snapshot analysis, the most useful resources are:

{PREFERRED_RESOURCES}

Patient ID:
{patient_id}

Clinical question:
{question}

Select the minimal FHIR resources required.

Return ONLY valid JSON:

{{
 "required_resources": ["Patient", "..."]
}}
"""

    response = llm.invoke(prompt)

    try:
        result = json.loads(response.content)

    except Exception:
        # Fallback if the model returns invalid JSON
        result = {"required_resources": PREFERRED_RESOURCES}

    resources = result.get("required_resources", [])

    # --------------------------------------------------
    # Safety: restrict to dataset resources
    # --------------------------------------------------

    resources = [
        r for r in resources if r in AVAILABLE_RESOURCES
    ]

    # --------------------------------------------------
    # Expand dependencies
    # --------------------------------------------------

    resources = expand_dependencies(resources)

    # --------------------------------------------------
    # Ensure Patient always included
    # --------------------------------------------------

    if "Patient" not in resources:
        resources.append("Patient")

    # --------------------------------------------------
    # Remove duplicates and keep stable order
    # --------------------------------------------------

    ordered_resources = []

    for r in AVAILABLE_RESOURCES:
        if r in resources:
            ordered_resources.append(r)

    result_state = {
        "required_resources": ordered_resources
    }

    debug_trace("requirement_llm2 (output)", result_state)

    return result_state