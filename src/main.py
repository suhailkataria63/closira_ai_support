from agent import SupportWorkflow


def main() -> None:
    workflow = SupportWorkflow()
    print("Closira Demo Assistant — Bloom Aesthetics Clinic")
    print("Type 'summary' to end the session and generate a structured summary.\n")

    while True:
        customer_message = input("Customer: ").strip()
        if not customer_message:
            continue
        if customer_message.lower() in {"summary", "exit", "quit"}:
            print("\nConversation Summary:")
            print(workflow.summarize())
            break

        response = workflow.handle_message(customer_message)
        print(f"AI: {response['answer']}")
        if response.get("next_question"):
            question = response["next_question"]
            print(f"AI Qualification Question: {question}")
            lead_answer = input("Customer: ").strip()
            workflow.store_lead_response(question, lead_answer)

        if response.get("escalation_required"):
            print(f"[Escalation flagged: {', '.join(response.get('escalation_reason', []))}]")


if __name__ == "__main__":
    main()
