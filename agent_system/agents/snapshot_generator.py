from typing import Dict, Any

from langchain_openai import ChatOpenAI

from agent_system.utils.debug_trace import debug_trace
from audit.decorator import audited_node


# --------------------------------------------------
# Initialize LLM
# --------------------------------------------------

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    max_tokens=3000,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def extract_patient_info(patient: Dict[str, Any]) -> str:

    if not patient:
        return "Unknown patient"

    name = ""

    names = patient.get("name", [])

    if names:
        given = " ".join(names[0].get("given", []))
        family = names[0].get("family", "")
        name = f"{given} {family}".strip()

    gender = patient.get("gender", "unknown")
    birth = patient.get("birthDate", "unknown")

    return f"{name} | Gender: {gender} | DOB: {birth}"


def extract_medications(medications):

    meds = []

    for med in medications:

        code = (
            med.get("medicationCodeableConcept", {})
            .get("text")
        )

        if not code:
            coding = med.get("medicationCodeableConcept", {}).get("coding", [])
            if coding:
                code = coding[0].get("display")

        if code:
            meds.append(code)

    return meds


def extract_allergies(allergies):

    allergy_list = []

    for a in allergies:

        code = (
            a.get("code", {})
            .get("text")
        )

        if not code:
            coding = a.get("code", {}).get("coding", [])
            if coding:
                code = coding[0].get("display")

        if code:
            allergy_list.append(code)

    return allergy_list


# --------------------------------------------------
# Snapshot Generator Node
# --------------------------------------------------
@audited_node
def snapshot_generator(state: Dict[str, Any]) -> Dict[str, Any]:

    debug_trace("snapshot_generator (input)", state)
    # safegaurd
    if "error" in state:
        return {"snapshot": state["error"]}

    aggregated = state.get("aggregated_data", {})

    patient = aggregated.get("patient")
    encounters = aggregated.get("er_encounters", [])
    medications = aggregated.get("er_medications", [])
    allergies = aggregated.get("allergies", [])

    patient_info = extract_patient_info(patient)

    medication_list = extract_medications(medications)

    allergy_list = extract_allergies(allergies)

    prompt = f"""
You are an emergency department clinical summarization assistant.

Generate a concise ER clinical snapshot using the structured data below.

Patient:
{patient_info}

Number of ER encounters:
{len(encounters)}

Medications recorded during ER encounter:
{medication_list}

Known allergies:
{allergy_list}

Instructions:
- Write a short ER clinical snapshot.
- Use clear clinical language.
- Avoid speculation.
- Only summarize the available information.
"""

    response = llm.invoke(prompt)

    snapshot = response.content

    result = {
        "snapshot": snapshot
    }

    debug_trace("snapshot_generator (output)", result)

    return result