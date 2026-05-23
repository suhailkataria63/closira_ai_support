import json
import os
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


SYSTEM_PROMPT = """
You are Closira Assistant for Bloom Aesthetics Clinic.
Your job is to support inbound customer conversations for an SMB using only the provided SOP.

Core rules:
1. Answer only from SOP data. Never invent prices, medical advice, policies, discounts, or services.
2. If the SOP does not contain the answer, say you do not have that information and escalate to a human.
3. Escalate immediately for complaints, medical questions, pricing negotiation, angry sentiment, explicit human-agent requests, low confidence, or more than two unanswered questions.
4. Keep tone friendly, concise, professional, and suitable for small business customer support.
5. Avoid robotic phrasing. Give short, natural answers that sound helpful but do not overpromise.
6. Ask structured lead qualification questions after answering the customer when appropriate.
7. Return outputs in valid JSON with these fields:
   answer: string
   confidence: number between 0 and 1
   used_sop_fields: list of strings
   out_of_scope: boolean
   escalation_required: boolean
   escalation_reason: list of strings
   next_question: string or null

SOP data:
{SOP_JSON}
"""


SUMMARY_PROMPT = """
You are summarizing a customer support conversation for Bloom Aesthetics Clinic.
Use only the provided conversation state and SOP context. Do not invent details.

Return valid JSON with these fields:
customer_intent: string
key_details_collected: object
sop_gaps_identified: list of strings
escalation_reasons: list of strings
recommended_next_action: string

SOP data:
{SOP_JSON}
"""


class SupportAgent:
    """Generates SOP-grounded support responses with a rule-based fallback."""

    def __init__(self, sop: Dict[str, Any], use_llm: bool = True) -> None:
        load_dotenv()
        self.sop = sop
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.use_llm = use_llm and bool(os.getenv("OPENAI_API_KEY")) and OpenAI is not None
        self.client = OpenAI() if self.use_llm else None

    def answer_faq(
        self,
        customer_message: str,
        conversation_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        if not self.use_llm:
            return self._fallback_answer(customer_message)

        try:
            return self._llm_answer(customer_message, conversation_messages or [])
        except Exception:
            return self._fallback_answer(customer_message)

    def next_lead_question(self, qualification_index: int) -> Optional[str]:
        questions = self.sop.get("lead_qualification_questions", [])
        if qualification_index >= len(questions):
            return None
        return questions[qualification_index]

    def generate_summary(
        self,
        messages: List[Dict[str, str]],
        lead_details: Dict[str, str],
        sop_gaps: List[str],
        escalation_reasons: List[str],
    ) -> Dict[str, Any]:
        if self.use_llm:
            try:
                return self._llm_summary(messages, lead_details, sop_gaps, escalation_reasons)
            except Exception:
                pass

        return self._fallback_summary(messages, lead_details, sop_gaps, escalation_reasons)

    def _fallback_summary(
        self,
        messages: List[Dict[str, str]],
        lead_details: Dict[str, str],
        sop_gaps: List[str],
        escalation_reasons: List[str],
    ) -> Dict[str, Any]:
        return {
            "customer_intent": self._infer_intent(messages),
            "key_details_collected": lead_details,
            "sop_gaps_identified": sop_gaps,
            "escalation_reasons": sorted(set(escalation_reasons)),
            "recommended_next_action": self._recommended_action(lead_details, escalation_reasons),
        }

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT.replace("{SOP_JSON}", json.dumps(self.sop, indent=2))

    def _summary_prompt(self) -> str:
        return SUMMARY_PROMPT.replace("{SOP_JSON}", json.dumps(self.sop, indent=2))

    def _llm_answer(self, customer_message: str, conversation_messages: List[Dict[str, str]]) -> Dict[str, Any]:
        assert self.client is not None
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._system_prompt()},
                *conversation_messages,
                {"role": "user", "content": customer_message},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def _llm_summary(
        self,
        messages: List[Dict[str, str]],
        lead_details: Dict[str, str],
        sop_gaps: List[str],
        escalation_reasons: List[str],
    ) -> Dict[str, Any]:
        assert self.client is not None
        conversation_state = {
            "messages": messages,
            "lead_details": lead_details,
            "sop_gaps": sop_gaps,
            "escalation_reasons": sorted(set(escalation_reasons)),
        }
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._summary_prompt()},
                {"role": "user", "content": json.dumps(conversation_state, indent=2)},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        summary = json.loads(content)
        return {
            "customer_intent": summary.get("customer_intent", self._infer_intent(messages)),
            "key_details_collected": summary.get("key_details_collected", lead_details),
            "sop_gaps_identified": summary.get("sop_gaps_identified", sop_gaps),
            "escalation_reasons": summary.get("escalation_reasons", sorted(set(escalation_reasons))),
            "recommended_next_action": summary.get(
                "recommended_next_action",
                self._recommended_action(lead_details, escalation_reasons),
            ),
        }

    def _fallback_answer(self, customer_message: str) -> Dict[str, Any]:
        text = customer_message.lower()
        used_fields: List[str] = []
        out_of_scope = False
        answer = ""
        confidence = 0.9

        services = self.sop.get("services", {})
        business_name = self.sop.get("business_name", "the clinic")

        if any(word in text for word in ["angry", "frustrated", "upset", "cancelled", "complaint"]):
            out_of_scope = True
            confidence = 0.25
            answer = "I am sorry this has been frustrating."
        elif "botox" in text and ("price" in text or "cost" in text):
            answer = f"Botox starts {services.get('Botox', 'from the SOP')} at {business_name}."
            used_fields = ["services.Botox"]
        elif "filler" in text and ("price" in text or "cost" in text):
            answer = f"Fillers start {services.get('Fillers', 'from the SOP')} at {business_name}."
            used_fields = ["services.Fillers"]
        elif "consultation" in text or "consult" in text:
            answer = f"Consultations are {services.get('Consultations', 'listed in the SOP')} at {business_name}."
            used_fields = ["services.Consultations"]
        elif "hour" in text or "open" in text or "timing" in text:
            answer = f"{business_name} is open {self.sop.get('hours', 'during the hours listed in the SOP')}."
            used_fields = ["hours"]
        elif "book" in text or "appointment" in text:
            answer = self.sop.get("booking", "You can book using the process listed in the SOP.")
            used_fields = ["booking"]
        elif "cancel" in text:
            answer = self.sop.get("cancellation_policy", "Please follow the cancellation policy listed in the SOP.")
            used_fields = ["cancellation_policy"]
        else:
            out_of_scope = True
            confidence = 0.25
            answer = "I do not have that detail in the clinic SOP, so I will pass this to a human team member."

        return {
            "answer": answer,
            "confidence": confidence,
            "used_sop_fields": used_fields,
            "out_of_scope": out_of_scope,
            "escalation_required": out_of_scope,
            "escalation_reason": ["low_confidence_or_out_of_scope"] if out_of_scope else [],
            "next_question": None,
        }

    def _infer_intent(self, messages: List[Dict[str, str]]) -> str:
        combined = " ".join(message["content"].lower() for message in messages if message["role"] == "user")
        if "botox" in combined:
            return "Asked about Botox service/pricing"
        if "filler" in combined:
            return "Asked about filler service/pricing"
        if "book" in combined or "appointment" in combined:
            return "Interested in booking an appointment"
        return "General customer enquiry"

    def _recommended_action(self, lead_details: Dict[str, str], escalation_reasons: List[str]) -> str:
        if escalation_reasons:
            return "Human agent should review and respond before continuing the conversation."
        if lead_details:
            return "Proceed with booking guidance through WhatsApp or website."
        return "Ask lead qualification questions and continue support."


def __getattr__(name: str) -> Any:
    if name == "SupportWorkflow":
        from workflow import SupportWorkflow

        return SupportWorkflow
    raise AttributeError(f"module 'agent' has no attribute {name!r}")
