"""
Prompts module for the reasoning engine.
This module defines all string templates and JSON schemas used to interact with
the AI models. Keeping prompts centralized ensures versionability, consistency,
and prevents prompt drift.

Schema v2: The LLM is instructed to return strict structured JSON objects
matching our typed Pydantic schemas. No markdown, no prose walls, no [1] citations.
"""

import json
from typing import Any, Dict, List

# -----------------------------------------------------------------------------
# JSON SCHEMA — STRICT STRUCTURED OUTPUT
# -----------------------------------------------------------------------------

EXPECTED_OUTPUT_JSON_SCHEMA = """{
  "summary": {
    "overview": "string — A comprehensive clinical synthesis of the case. Write 3-8 paragraphs of specialist-level narrative. Synthesize findings, weigh evidence, explain contradictions, and discuss uncertainty. DO NOT use markdown. DO NOT use [1] style citations. DO NOT include citations. Write like an attending physician's assessment.",
    "severity": "string — Must be exactly one of: 'low', 'moderate', 'high', 'critical'"
  },
  "supporting_findings": [
    {
      "finding": "string — The clinical finding (e.g. 'Positive ANA at 1:640')",
      "explanation": "string — 2-4 sentences explaining how this finding supports the clinical picture, its pathophysiological significance, and diagnostic weight",
      "strength": "string — Must be exactly one of: 'weak', 'moderate', 'strong'"
    }
  ],
  "contradictory_findings": [
    {
      "finding": "string — The contradictory clinical finding",
      "explanation": "string — 2-4 sentences explaining why this finding contradicts or complicates the primary assessment",
      "significance": "string — Brief statement of how significant this contradiction is for the overall assessment"
    }
  ],
  "differentials": [
    {
      "diagnosis": "string — Name of the differential diagnosis",
      "reasoning_confidence": "number — A decimal between 0.0 and 1.0 representing how coherent the clinical hypothesis is (e.g. 0.85 for highly coherent, 0.45 for moderate). If confidence is low, clearly state 'low confidence' in the reasoning rather than forcing precision.",
      "evidence_confidence": "number — A decimal between 0.0 and 1.0 representing how strong the literature support is for this hypothesis.",
      "certainty_tier": "string — Must be exactly one of: 'possible', 'likely', 'highly likely', 'provisional classification-compatible', 'confirmed only if strict conditions are fully met'.",
      "is_provisional": "boolean — True if the diagnosis requires repeat testing, longitudinal confirmation, or explicit classification thresholds that are not yet met.",
      "reasoning": "string — 3-6 sentences of specialist-level clinical reasoning for this diagnosis. Explain the pathophysiology, epidemiology, and how the clinical data maps to this diagnosis. Reference specific patient findings. Use cautious language ('consistent with', 'suggestive of', 'raises concern for'). Avoid 'confirmed', 'diagnostic for', 'proves', 'definitive' unless strict conditions are met.",
      "supporting_evidence": ["string — List of specific patient findings supporting this diagnosis"],
      "contradictory_evidence": ["string — List of specific patient findings or missing data arguing against this diagnosis. Do not suppress uncertainty."]
    }
  ],
  "next_steps": [
    {
      "title": "string — Concise action title (e.g. 'Urgent Rheumatology Consultation')",
      "category": "string — Must be exactly one of: 'diagnostic', 'monitoring', 'treatment', 'referral', 'follow_up'",
      "rationale": "string — 2-5 sentences of specialist-level reasoning. Explain WHY this step is recommended, how it connects to the differential, what information gap it fills, and what clinical decision it enables. This should read like a specialist consult recommendation.",
      "urgency": "string — Must be exactly one of: 'routine', 'urgent', 'emergent'",
      "expected_outcome": "string — What the clinician should expect from this step and how results will inform management",
      "risks_of_delay": "string or null — If urgency is 'urgent' or 'emergent', explain the clinical consequences of delaying this step"
    }
  ],
  "missing_information": [
    {
      "item": "string — The specific missing data element (e.g. 'Complement levels (C3/C4)')",
      "category": "string — Must be exactly one of: 'history', 'labs', 'medications', 'imaging', 'risk_factors', 'family_history', 'physical_exam'",
      "why_it_matters": "string — 2-4 sentences explaining the clinical significance of this missing data, including pathophysiological relevance",
      "impact_on_assessment": "string — 2-3 sentences describing how the absence of this data limits the current assessment and confidence levels",
      "possible_implications": "string — 2-3 sentences describing how the management plan might change if this information were available"
    }
}"""

# -----------------------------------------------------------------------------
# SYSTEM PROMPTS
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an advanced clinical reasoning assistant embedded in a professional clinical decision-support platform. Your purpose is to assist medical professionals by synthesizing clinical data, suggesting differential diagnoses, and highlighting important clinical patterns.

ROLE & SCOPE:
- You are a non-diagnostic educational tool. You do not make final medical decisions. Never present the system as a doctor or as making a definitive diagnosis.
- Acknowledge uncertainty explicitly. If data is missing or ambiguous, state so in the appropriate sections.
- Maintain a professional, objective tone resembling attending physician documentation or specialist consult notes. Keep the output medically cautious, evidence-based, and suitable for educational use only.
- Prefer "consistent with," "suggestive of," "supports," and "raises concern for." Avoid "confirmed" unless the available data truly justifies it.
- Distinguish between clinical suspicion, evidence support, missing confirmatory information, differential diagnoses, and uncertainty.
- If the presentation is high-risk or time-sensitive, recommend urgent specialist review in educational language.

OUTPUT FORMAT — STRICT REQUIREMENTS:
1. You MUST return your response as a SINGLE valid JSON object matching the provided schema EXACTLY.
2. Do NOT wrap the JSON in markdown code fences (no ```json).
3. Do NOT include any text before or after the JSON object.
4. Ensure perfect JSON validity: properly escape quotes, newlines, and special characters within strings.

INLINE CITATIONS:
- NEVER use [1], [2] style citations.
- DO NOT invent references inline or add {{cite:ID}} during this generation pass. Citations will be added later by a separate verification pipeline.

CLINICAL REASONING DEPTH:
- The overview in the summary must be 3-8 paragraphs of specialist-level synthesis.
- Each differential must include 3-6 sentences of reasoning with specific patient findings.
- Each next step must include 2-5 sentences of specialist rationale — not just "consult rheumatology".
- Each missing information item must explain WHY it matters, HOW it affects confidence, and WHAT changes if obtained.
- Synthesize — do not dump textbook content.
- Weigh evidence explicitly. Discuss uncertainty. Include contradictory findings, not only supporting ones. Avoid confirmation bias. Search for both supporting and opposing evidence.
- Avoid repetitive AI phrasing ("It is important to note...").
- Write like a specialist consultant, not a chatbot.

SEVERITY ASSESSMENT:
- Evaluate overall clinical severity based on the totality of findings.
- 'low': stable, non-urgent findings, limited systemic involvement
- 'moderate': concerning findings requiring timely workup
- 'high': significant multi-system involvement, urgent workup required
- 'critical': life-threatening, requires immediate intervention

CONFIDENCE SCORING:
- Maintain two separate internal concepts: reasoning confidence (how coherent the clinical hypothesis is) and evidence confidence (how strong the literature support is). Do not merge them into one hidden assumption.
- Use numeric 0.0–1.0 scores for reasoning_confidence and evidence_confidence in differentials.
- 0.0–0.25: unlikely but worth considering
- 0.25–0.50: possible, requires further workup
- 0.50–0.75: probable, supported by multiple findings
- 0.75–1.0: highly likely, strong evidence convergence
- If confidence is low, say "low confidence" rather than forcing precision.

EVIDENCE STRENGTH:
- 'strong': directly confirmed by objective data (lab, imaging, pathology)
- 'moderate': supported by clinical correlation and pattern recognition
- 'weak': suggestive but could have multiple explanations
"""

# -----------------------------------------------------------------------------
# USER PROMPT TEMPLATES
# -----------------------------------------------------------------------------

REASONING_PROMPT_TEMPLATE = """Please analyze the following clinical case and provide a structured reasoning report.

## Preprocessing Engine Summary
{preprocessing_summary}

## Clinical Data
### Anamnesis
{anamnesis_text}

### Physical Exam
{physical_exam_text}

### Laboratory Results
{laboratory_text}

### Imaging & Morphology
{morphological_text}

## Follow-up Context
{follow_up_context}

## Previous Differential Diagnoses
{previous_differentials}

## Output Format
You MUST return your response as a valid JSON object exactly matching this schema:
{json_schema}

CRITICAL RULES:
- Return ONLY the JSON object. No markdown, no code fences, no explanatory text.
- Every text field must be substantive (no one-line placeholders).
- The summary overview must be 3-8 paragraphs of specialist-level synthesis.
- DO NOT invent or include any citations or citation tokens.
- Each next_step rationale must be 2-5 sentences of specialist reasoning.
- Each missing_information entry must fully explain clinical significance.
- Assign numeric confidence scores to differentials (0.0-1.0).
- Categorize next_steps and missing_information with the specified enum values.
"""

GROUNDING_QUERY_TEMPLATE = """Formulate a search query to retrieve medical evidence for the following clinical question, given the context.

## Clinical Context
{context_summary}

## Clinical Question
{clinical_question}

Return only the search query string, optimized for a medical literature database.
"""

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def _format_physical_exam(exam: Any) -> str:
    """
    Formats the physical exam dict into a readable clinical narrative block
    with labeled sections, so the AI can reason over each system explicitly.
    Skips empty/None fields.
    """
    if not exam:
        return "No physical exam findings provided."

    # Map field keys to display labels
    FIELD_LABELS = {
        "general_appearance": "General Appearance",
        "heent":              "HEENT",
        "neck":               "Neck",
        "cardiovascular":     "Cardiovascular",
        "respiratory":        "Respiratory",
        "vascular":           "Vascular / Peripheral Perfusion",
        "abdominal":          "Abdominal",
        "genitourinary":      "Genitourinary",
        "neurologic":         "Neurologic",
        "psychiatric":        "Psychiatric / Mental Status",
        "endocrine":          "Endocrine",
        "dermatologic":       "Dermatologic",
        "lymphatic":          "Lymphatic",
        "musculoskeletal":    "Musculoskeletal",
        "breast":             "Breast Exam",
        "pelvic":             "Pelvic Exam",
        "rectal":             "Rectal Exam",
    }

    exam_dict = exam if isinstance(exam, dict) else {}
    lines = []
    for key, label in FIELD_LABELS.items():
        val = exam_dict.get(key)
        if val and str(val).strip():
            lines.append(f"  {label}: {str(val).strip()}")

    return "\n".join(lines) if lines else "No physical exam findings provided."


def _format_anamnesis(anamnesis: Any) -> str:
    """
    Formats the anamnesis dict into a readable labeled clinical block.
    Skips empty/None fields.
    """
    if not anamnesis:
        return "No anamnesis provided."

    FIELD_LABELS = {
        "chief_complaint":              "Chief Complaint",
        "history_of_present_illness":   "History of Present Illness",
        "past_medical_history":         "Past Medical History",
        "medications":                  "Medications",
        "allergies":                    "Allergies",
        "family_history":               "Family History",
        "social_history":               "Social History",
        "travel_history":               "Travel History",
        "constitutional_symptoms":      "Constitutional Symptoms",
    }

    anam_dict = anamnesis if isinstance(anamnesis, dict) else {}
    lines = []
    for key, label in FIELD_LABELS.items():
        val = anam_dict.get(key)
        if val and str(val).strip():
            lines.append(f"  {label}: {str(val).strip()}")

    return "\n".join(lines) if lines else "No anamnesis provided."


def format_reasoning_prompt(
    preprocessing_result: str,
    clinical_data: Dict[str, Any],
    follow_up_context: str,
    previous_differentials: str
) -> str:
    """
    Fills the reasoning prompt template with structured clinical inputs.
    
    Args:
        preprocessing_result: Summary from the preprocessing engine.
        clinical_data: Dictionary containing anamnesis, physical_exam, labs, and morphology.
        follow_up_context: Additional context from follow-up entries.
        previous_differentials: Previously generated differential diagnoses.
        
    Returns:
        The fully formatted prompt string ready for the AI model.
    """
    # Format anamnesis as labeled sections
    anamnesis_raw = clinical_data.get("anamnesis", {})
    anamnesis_text = _format_anamnesis(anamnesis_raw)

    # Format physical exam as labeled sections instead of raw JSON
    physical_exam_raw = clinical_data.get("physical_exam", {})
    physical_exam_text = _format_physical_exam(physical_exam_raw)
    
    # Simple formatting for labs and morphology if they are dicts or lists
    labs = clinical_data.get("labs", "No laboratory results provided.")
    laboratory_text = json.dumps(labs, indent=2) if isinstance(labs, (dict, list)) else str(labs)
    
    morph = clinical_data.get("morphology", "No morphological findings provided.")
    morphological_text = json.dumps(morph, indent=2) if isinstance(morph, (dict, list)) else str(morph)
    
    return REASONING_PROMPT_TEMPLATE.format(
        preprocessing_summary=preprocessing_result or "None",
        anamnesis_text=anamnesis_text,
        physical_exam_text=physical_exam_text,
        laboratory_text=laboratory_text,
        morphological_text=morphological_text,
        follow_up_context=follow_up_context or "None",
        previous_differentials=previous_differentials or "None",
        json_schema=EXPECTED_OUTPUT_JSON_SCHEMA
    )


def format_grounding_query(diagnoses: List[str], context: str) -> str:
    """
    Fills the grounding query template to generate an evidence retrieval query.
    
    Args:
        diagnoses: List of current top differential diagnoses to investigate.
        context: Brief clinical context summarizing the patient's state.
        
    Returns:
        The formatted grounding query prompt.
    """
    clinical_question = f"What is the latest evidence regarding the diagnosis, differentiation, and management of: {', '.join(diagnoses)}?"
    
    return GROUNDING_QUERY_TEMPLATE.format(
        clinical_question=clinical_question,
        context_summary=context or "No context provided."
    )
