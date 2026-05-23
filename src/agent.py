import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from escalation import detect_escalation
from logger import ConversationLogger
from sop_loader import load_sop


SYSTEM_PROMPT = """
You are Closira Assistant for Bloom Aesthetics Clinic.
Your job is to support inbound customer conversations for an SMB using only the provided SOP.

Core rules:
1. Answer only from SOP data. Never invent prices, medical advice, policies, discounts, or services.
2. If the SOP does not contain the answer, say you do not have that information and escalate to a human.
3. Escalate immediately for complaints, medical questions, pricing negotiation, angry sentiment, explicit human-agent requests, low confidence, or more than two unanswered questions.
4. Keep tone warm, concise, professional, and suitable for a small business customer support assistant.
5. Ask structured lead qualification questions after answering the customer when appropriate.
6. Return outputs in valid JSON with these fields:
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


@dataclass
class ConversationState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    lead_details: Dict[str, str] = field(default_factory=dict)
    unanswered_count: int = 0
    escalation_reasons: List[str] = field(default_factory=list)
    sop_gaps: List[str] = field(default_factory=list)


class SupportWorkflow:
    def __init__(self, sop_path: str = "data/sop.json", use_llm: bool = True) -> None:
        load_dotenv()
        self.sop = load_sop(sop_path)
        self.state = ConversationState()
        self.logger = ConversationLogger()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.use_llm = use_llm and bool(os.getenv("OPENAI_API_KEY"))
        self.client: Optional[OpenAI] = OpenAI() if self.use_llm else None
        self.qualification_index = 0

    def _system_prompt(self) -> str:
        return SYSTEM_PROMPT.replace("{SOP_JSON}", json.dumps(self.sop, indent=2))

    def _fallback_answer(self, customer_message: str) -> Dict[str, Any]:
        """Rule-based fallback for demo/testing when no API key is configured."""
        text = customer_message.lower()
        used_fields: List[str] = []
        out_of_scope = False
        answer = ""
        confidence = 0.9

        if "botox" in text and ("price" in text or "cost" in text):
            answer = "Botox starts from £200 at Bloom Aesthetics Clinic."
            used_fields = ["services.Botox"]
        elif "filler" in text and ("price" in text or "cost" in text):
            answer = "Fillers start from £250 at Bloom Aesthetics Clinic."
            used_fields = ["services.Fillers"]
        elif "consultation" in text or "consult" in text:
            answer = "Consultations are free at Bloom Aesthetics Clinic."
            used_fields = ["services.Consultations"]
        elif "hour" in text or "open" in text or "timing" in text:
            answer = "Bloom Aesthetics Clinic is open Monday to Saturday, 9 am to 7 pm."
            used_fields = ["hours"]
        elif "book" in text or "appointment" in text:
            answer = "Bookings can be made via WhatsApp or the website."
            used_fields = ["booking"]
        elif "cancel" in text:
            answer = "Bloom Aesthetics Clinic requires 24 hours cancellation notice."
            used_fields = ["cancellation_policy"]
        else:
            out_of_scope = True
            confidence = 0.25
            answer = "I do not have that information in the clinic SOP, so I will hand this over to a human team member."

        next_question = None
        if not out_of_scope and self.qualification_index < len(self.sop["lead_qualification_questions"]):
            next_question = self.sop["lead_qualification_questions"][self.qualification_index]
            self.qualification_index += 1

        return {
            "answer": answer,
            "confidence": confidence,
            "used_sop_fields": used_fields,
            "out_of_scope": out_of_scope,
            "escalation_required": out_of_scope,
            "escalation_reason": ["low_confidence_or_out_of_scope"] if out_of_scope else [],
            "next_question": next_question,
        }

    def _llm_answer(self, customer_message: str) -> Dict[str, Any]:
        assert self.client is not None
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self._system_prompt()},
                *self.state.messages,
                {"role": "user", "content": customer_message},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def handle_message(self, customer_message: str) -> Dict[str, Any]:
        first_pass = self._fallback_answer(customer_message) if not self.use_llm else self._llm_answer(customer_message)
        low_confidence = first_pass.get("confidence", 0) < 0.65 or first_pass.get("out_of_scope", False)
        escalation = detect_escalation(customer_message, self.state.unanswered_count, low_confidence)

        if first_pass.get("out_of_scope"):
            self.state.unanswered_count += 1
            self.state.sop_gaps.append(customer_message)
        else:
            self.state.unanswered_count = 0

        reasons = sorted(set(first_pass.get("escalation_reason", []) + escalation.reasons))
        first_pass["escalation_required"] = first_pass.get("escalation_required", False) or escalation.should_escalate
        first_pass["escalation_reason"] = reasons

        if first_pass["escalation_required"] and not first_pass["answer"].lower().startswith("i do not"):
            first_pass["answer"] += " I will hand this over to a human team member so you get the right support."

        self.state.messages.append({"role": "user", "content": customer_message})
        self.state.messages.append({"role": "assistant", "content": first_pass["answer"]})
        self.state.escalation_reasons.extend(reasons)

        self.logger.write("customer_message", {"message": customer_message})
        self.logger.write("assistant_response", first_pass)

        return first_pass

    def store_lead_response(self, question: str, answer: str) -> None:
        self.state.lead_details[question] = answer
        self.logger.write("lead_detail_collected", {"question": question, "answer": answer})

    def summarize(self) -> Dict[str, Any]:
        summary = {
            "customer_intent": self._infer_intent(),
            "key_details_collected": self.state.lead_details,
            "sop_gaps_identified": self.state.sop_gaps,
            "escalation_reasons": sorted(set(self.state.escalation_reasons)),
            "recommended_next_action": self._recommended_action(),
        }
        self.logger.write("conversation_summary", summary)
        return summary

    def _infer_intent(self) -> str:
        combined = " ".join(message["content"].lower() for message in self.state.messages if message["role"] == "user")
        if "botox" in combined:
            return "Asked about Botox service/pricing"
        if "filler" in combined:
            return "Asked about filler service/pricing"
        if "book" in combined or "appointment" in combined:
            return "Interested in booking an appointment"
        return "General customer enquiry"

    def _recommended_action(self) -> str:
        if self.state.escalation_reasons:
            return "Human agent should review and respond before continuing the conversation."
        if self.state.lead_details:
            return "Proceed with booking guidance through WhatsApp or website."
        return "Ask lead qualification questions and continue support."
