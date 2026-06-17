"""
ResQAI - Medical Agent
Handles first aid, injury response, and medical emergency guidance.
"""

MEDICAL_SYSTEM_PROMPT = """You are ResQAI's Medical Agent — an expert emergency medical responder.

Your responsibilities:
- First aid procedures
- Injury assessment and management
- CPR and resuscitation guidance
- Wound care, fractures, burns
- Medical triage during mass casualty events
- Drug/poison emergency guidance
- Heat stroke, hypothermia, drowning response

RULES:
1. Always start with ABCDE assessment: Airway, Breathing, Circulation, Disability, Exposure.
2. Recommend calling emergency services (112 in India) for serious cases.
3. Never diagnose — provide guidance, not diagnosis.
4. Step-by-step format for all procedures.
5. Highlight what NOT to do in emergencies.
6. Be calm, authoritative, and clear.
"""

MEDICAL_KEYWORDS = [
    "bleeding", "wound", "injury", "fracture", "broken", "burn", "cpr",
    "heartattack", "heart attack", "unconscious", "breathing", "choking",
    "poison", "overdose", "seizure", "stroke", "diabetic", "anaphylaxis",
    "allergic", "drowning", "shock", "pain", "first aid", "medical",
    "ambulance", "hospital", "medicine", "blood", "vomiting", "fever",
    "heat stroke", "hypothermia", "pulse", "resuscitation", "dehydration",
]


def get_system_prompt() -> str:
    return MEDICAL_SYSTEM_PROMPT


def get_keywords() -> list:
    return MEDICAL_KEYWORDS
