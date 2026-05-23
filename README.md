# Closira AI Customer Support Workflow Assignment

This project is a Python-based AI customer support workflow for a fictional SMB: **Bloom Aesthetics Clinic**. It demonstrates FAQ answering from SOP data, lead qualification, escalation detection, and structured conversation summarization.

## Features

- SOP grounded answering
- Lead qualification
- Escalation detection
- Structured conversation summary
- OpenAI integration
- Safe fallback mode
- Answers customer questions only from the provided SOP
- Avoids hallucinating unsupported facts
- Detects escalation triggers such as complaints, medical questions, pricing negotiation, angry sentiment, explicit human request, low confidence, and out-of-scope questions
- Logs conversation events and escalation reasons

## Project Structure

```text
closira_ai_support_assignment/
├── data/
│   └── sop.json
├── logs/
│   └── .gitkeep
├── src/
│   ├── agent.py
│   ├── escalation.py
│   ├── logger.py
│   ├── main.py
│   ├── sop_loader.py
│   └── workflow.py
├── test_transcripts/
│   ├── 01_in_sop_question.md
│   ├── 02_out_of_scope_question.md
│   ├── 03_escalation_trigger.md
│   ├── 04_lead_qualification.md
│   └── 05_conversation_summary.md
├── .env.example
├── .gitignore
├── prompt_design.md
├── README.md
└── requirements.txt
```

## SOP Data

The workflow uses `data/sop.json` as its knowledge source. The current SOP is for Bloom Aesthetics Clinic:

- Hours: Monday to Saturday, 9 am to 7 pm
- Services: Botox from £200, fillers from £250, consultations free
- Booking: WhatsApp or website
- Cancellation: 24 hours notice required
- Escalate for complaints, medical questions, pricing negotiation, or more than two unanswered questions

## Setup

```bash
git clone <your-github-repo-url>
cd closira_ai_support_assignment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API key in `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## OpenAI Setup

The app uses the OpenAI API when `OPENAI_API_KEY` is available. To run with OpenAI:

```bash
cp .env.example .env
```

Add your local key to `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Then install dependencies and start the CLI:

```bash
pip install -r requirements.txt
python src/main.py
```

Do not commit `.env`; it is ignored by git. If no API key is provided, the project still runs in rule-based fallback demo mode so the assignment can be tested reliably without external API access.

## Run the Workflow

```bash
python src/main.py
```

Type customer messages in the CLI. Type `summary` to end the conversation and generate the final structured summary.

## Example

```text
Customer: What are your Botox prices?
AI: Botox starts from £200 at Bloom Aesthetics Clinic.
AI Qualification Question: Which service are you interested in: Botox, fillers, or consultation?
Customer: Botox
Customer: summary
```

## Logs

Conversation logs are written to:

```text
logs/conversation_log.jsonl
```

Each log entry includes timestamp, event type, and payload.

## Test Transcripts

The `test_transcripts/` folder contains sample conversations for all required behaviours:

1. In-SOP question
2. Out-of-scope question
3. Escalation trigger
4. Lead qualification
5. Conversation summary

## Known Limitations

- The prototype uses keyword-based escalation checks in addition to LLM output.
- It does not include a frontend UI because the assignment allows a CLI/script-based prototype.
- It does not schedule real bookings; it only guides the user based on SOP instructions.
- Medical questions are escalated instead of answered.
