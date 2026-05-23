from dataclasses import dataclass
from typing import List


@dataclass
class EscalationResult:
    should_escalate: bool
    reasons: List[str]


ANGRY_KEYWORDS = [
    "angry", "frustrated", "annoyed", "upset", "terrible", "bad service",
    "complaint", "unhappy", "refund", "furious", "waste of time"
]

HUMAN_KEYWORDS = [
    "human", "agent", "manager", "representative", "call me", "speak to someone"
]

MEDICAL_KEYWORDS = [
    "side effect", "safe", "allergy", "pregnant", "medicine", "medical", "diagnosis",
    "infection", "pain", "swelling", "risk", "doctor"
]

NEGOTIATION_KEYWORDS = [
    "discount", "negotiate", "cheaper", "lowest price", "price match", "bargain"
]


def detect_escalation(message: str, unanswered_count: int = 0, low_confidence: bool = False) -> EscalationResult:
    text = message.lower()
    reasons: List[str] = []

    if any(keyword in text for keyword in ANGRY_KEYWORDS):
        reasons.append("angry_or_frustrated_sentiment")
    if any(keyword in text for keyword in HUMAN_KEYWORDS):
        reasons.append("explicit_human_request")
    if any(keyword in text for keyword in MEDICAL_KEYWORDS):
        reasons.append("medical_question")
    if any(keyword in text for keyword in NEGOTIATION_KEYWORDS):
        reasons.append("pricing_negotiation")
    if unanswered_count > 2:
        reasons.append("more_than_two_unanswered_questions")
    if low_confidence:
        reasons.append("low_confidence_or_out_of_scope")

    return EscalationResult(should_escalate=bool(reasons), reasons=reasons)
