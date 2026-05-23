# Closira AI Customer Support Workflow Assignment

## Description

This project is a terminal-based AI customer support workflow for a fictional SMB, **Bloom Aesthetics Clinic**. It demonstrates how an assistant can answer FAQ-style questions from an SOP, qualify leads, detect escalation triggers, and produce a structured conversation summary.

The workflow can use the OpenAI API when an API key is configured. If no key is available, it still runs in a deterministic fallback mode for reliable demos and testing.

## Assignment Objective

Build a lightweight customer support assistant that follows a provided SOP, avoids unsupported answers, collects lead qualification details, escalates risky or out-of-scope conversations, and summarizes the interaction for a human team member.

## Features

- SOP-grounded FAQ answering
- Lead qualification with 3 structured questions
- Escalation detection
- Structured conversation summary
- OpenAI API integration
- Safe fallback mode

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

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key locally in `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Run the CLI:

```bash
python3 src/main.py
```

Do not commit `.env`. It is ignored by git.

## Testing Scenarios

Run the app with `python3 src/main.py`, then try the following scenarios.

### In-SOP Question

```text
Customer: What are your Botox prices?
```

Expected: the assistant answers from the SOP, for example: `Botox starts from £200 at Bloom Aesthetics Clinic.`

### Out-of-Scope Question

```text
Customer: Do you offer laser hair removal?
```

Expected: the assistant does not guess, identifies that the information is not in the SOP, and triggers escalation.

### Complaint or Frustration

```text
Customer: I am very angry. My appointment was cancelled and nobody helped me.
```

Expected: the assistant acknowledges frustration and triggers escalation.

### Medical Question

```text
Customer: Is Botox safe if I am pregnant?
```

Expected: the assistant escalates instead of giving medical advice.

### Lead Qualification

After a valid in-SOP answer, the assistant asks exactly three structured questions:

```text
To help you better, may I ask:
- Which service are you interested in: Botox, fillers, or consultation?
Customer: Botox
To help you better, may I ask:
- Have you visited Bloom Aesthetics Clinic before?
Customer: No
To help you better, may I ask:
- What is your preferred booking channel: WhatsApp or website?
Customer: WhatsApp
```

### Conversation Summary

Type:

```text
Customer: summary
```

Expected: the app prints a formatted summary with customer intent, collected details, SOP gaps, escalation reasons, and recommended next action.

Additional sample runs are documented in `test_transcripts/`.

## Logs

Conversation events are written to:

```text
logs/conversation_log.jsonl
```

The log file is ignored by git.

## Known Limitations and Trade-Offs

- CLI only; there is no frontend.
- The SOP is intentionally small for assignment clarity.
- Fallback mode is deterministic and demo-oriented, so it is less flexible than the OpenAI path.
- OpenAI responses may vary slightly, but they must remain SOP-grounded.
- Escalation detection uses keyword/rule checks alongside model output, which improves reliability but may miss subtle phrasing.
