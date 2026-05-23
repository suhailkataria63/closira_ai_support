from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agent import SupportAgent
from escalation import detect_escalation
from logger import ConversationLogger
from sop_loader import load_sop


@dataclass
class ConversationState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    lead_details: Dict[str, str] = field(default_factory=dict)
    unanswered_count: int = 0
    escalation_reasons: List[str] = field(default_factory=list)
    sop_gaps: List[str] = field(default_factory=list)
    qualification_index: int = 0


class SupportWorkflow:
    """Runs the four assignment stages for the terminal support demo."""

    def __init__(self, sop_path: str = "data/sop.json", use_llm: bool = True) -> None:
        self.sop = load_sop(sop_path)
        self.agent = SupportAgent(self.sop, use_llm=use_llm)
        self.state = ConversationState()
        self.logger: Optional[ConversationLogger] = self._build_logger()

    def handle_message(self, customer_message: str) -> Dict[str, Any]:
        response = self.run_stage_1_faq_answering(customer_message)
        response = self.run_stage_3_escalation_detection(customer_message, response)
        response["next_question"] = self.run_stage_2_lead_qualification(response)

        self.state.messages.append({"role": "user", "content": customer_message})
        self.state.messages.append({"role": "assistant", "content": response["answer"]})

        self._log("customer_message", {"message": customer_message})
        self._log("assistant_response", response)
        return response

    def run_stage_1_faq_answering(self, customer_message: str) -> Dict[str, Any]:
        response = self.agent.answer_faq(customer_message, self.state.messages)
        if response.get("out_of_scope"):
            self.state.unanswered_count += 1
            self.state.sop_gaps.append(customer_message)
        else:
            self.state.unanswered_count = 0
        return response

    def run_stage_2_lead_qualification(self, response: Dict[str, Any]) -> Optional[str]:
        if response.get("out_of_scope") or response.get("escalation_required"):
            return None

        next_question = self.agent.next_lead_question(self.state.qualification_index)
        if next_question is not None:
            self.state.qualification_index += 1
        return next_question

    def run_stage_3_escalation_detection(self, customer_message: str, response: Dict[str, Any]) -> Dict[str, Any]:
        low_confidence = response.get("confidence", 0) < 0.65 or response.get("out_of_scope", False)
        escalation = detect_escalation(customer_message, self.state.unanswered_count, low_confidence)
        reasons = sorted(set(response.get("escalation_reason", []) + escalation.reasons))

        response["escalation_required"] = response.get("escalation_required", False) or escalation.should_escalate
        response["escalation_reason"] = reasons

        if response["escalation_required"] and not response["answer"].lower().startswith("i do not"):
            response["answer"] += " I will hand this over to a human team member so you get the right support."

        self.state.escalation_reasons.extend(reasons)
        if reasons:
            self._log("escalation_detected", {"reasons": reasons, "message": customer_message})
        return response

    def store_lead_response(self, question: str, answer: str) -> None:
        self.state.lead_details[question] = answer
        self._log("lead_detail_collected", {"question": question, "answer": answer})

    def run_stage_4_conversation_summary(self) -> Dict[str, Any]:
        summary = self.agent.generate_summary(
            self.state.messages,
            self.state.lead_details,
            self.state.sop_gaps,
            self.state.escalation_reasons,
        )
        self._log("conversation_summary", summary)
        return summary

    def summarize(self) -> Dict[str, Any]:
        return self.run_stage_4_conversation_summary()

    def _build_logger(self) -> Optional[ConversationLogger]:
        try:
            return ConversationLogger()
        except Exception:
            return None

    def _log(self, event_type: str, payload: Dict[str, Any]) -> None:
        if self.logger is None:
            return
        try:
            self.logger.write(event_type, payload)
        except Exception:
            pass
