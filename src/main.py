from workflow import SupportWorkflow


DIVIDER = "-" * 50


def print_list(title: str, items: object) -> None:
    print(f"{title}:")
    if not items:
        print("- None")
        return

    if isinstance(items, dict):
        for key, value in items.items():
            print(f"- {format_detail_label(key)}: {value}")
        return

    for item in items:
        print(f"- {item}")


def format_detail_label(label: str) -> str:
    key_labels = {
        "interested_service": "Interested service",
        "previous_visit_status": "Previous visit status",
        "preferred_booking_channel": "Preferred booking channel",
    }
    if label in key_labels:
        return key_labels[label]

    normalized = label.strip().rstrip("?")
    lower_label = normalized.lower()

    if "which service" in lower_label:
        return "Interested service"
    if "visited" in lower_label:
        return "Previous visit status"
    if "whatsapp" in lower_label or "website" in lower_label:
        return "Preferred booking channel"

    return normalized


def print_summary(summary: dict) -> None:
    print(DIVIDER)
    print("Conversation Summary")
    print(DIVIDER)
    print("Customer Intent:")
    print(summary.get("customer_intent", "Not captured"))
    print()

    print_list("Key Details Collected", summary.get("key_details_collected", {}))
    print()
    print_list("SOP Gaps Identified", summary.get("sop_gaps_identified", []))
    print()
    print_list("Escalation Reasons", summary.get("escalation_reasons", []))
    print()

    print("Recommended Next Action:")
    print(summary.get("recommended_next_action", "Continue the conversation."))
    print(DIVIDER)


def print_escalation(reasons: list) -> None:
    print(DIVIDER)
    print("Escalation Triggered")
    print("Reason(s):")
    if reasons:
        for reason in reasons:
            print(f"- {reason}")
    else:
        print("- unspecified")
    print(DIVIDER)


def collect_lead_answers(workflow: SupportWorkflow, first_question: str) -> None:
    question = first_question
    while question:
        print("To help you better, may I ask:")
        print(f"- {question}")
        lead_answer = input("Customer: ").strip()
        workflow.store_lead_response(question, lead_answer)
        question = workflow.next_lead_question()


def main() -> None:
    workflow = SupportWorkflow()
    print("Closira Demo Assistant - Bloom Aesthetics Clinic")
    print("Type 'summary' to end the session and generate a structured summary.\n")

    while True:
        customer_message = input("Customer: ").strip()
        if not customer_message:
            continue
        if customer_message.lower() in {"summary", "exit", "quit"}:
            print()
            print_summary(workflow.summarize())
            break

        response = workflow.handle_message(customer_message)
        print(f"AI: {response['answer']}")
        if response.get("next_question"):
            collect_lead_answers(workflow, response["next_question"])

        if response.get("escalation_required"):
            print_escalation(response.get("escalation_reason", []))


if __name__ == "__main__":
    main()
