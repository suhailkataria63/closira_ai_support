# VS Code + Codex Prompts

Use these prompts in order inside VS Code/Codex.

## Prompt 1 — Create Project Structure

Create a Python CLI project for an AI customer support workflow internship assignment. The project should have folders: src, data, logs, and test_transcripts. Add README.md, prompt_design.md, requirements.txt, .env.example, and .gitignore. The workflow should support FAQ answering from SOP data, lead qualification, escalation detection, and conversation summary.

## Prompt 2 — Implement SOP Loader and Escalation Logic

Create src/sop_loader.py to load data/sop.json. Create src/escalation.py with deterministic escalation detection for angry sentiment, complaints, explicit human request, medical questions, pricing negotiation, low confidence, out-of-scope questions, and more than two unanswered questions.

## Prompt 3 — Implement Main Agent Workflow

Create src/agent.py with a SupportWorkflow class. It should load the SOP, create a system prompt, call OpenAI if an API key exists, and fallback to rule-based answering if no API key exists. The model must answer only from SOP data, return JSON, ask qualification questions, log escalation reasons, and generate a structured summary.

## Prompt 4 — Implement CLI

Create src/main.py. The CLI should accept customer messages, print AI responses, ask lead qualification questions, store lead responses, flag escalation reasons, and generate a summary when the user types summary.

## Prompt 5 — Add Documentation and Test Transcripts

Create prompt_design.md explaining the system prompt, hallucination prevention, confidence-based escalation, tone/persona, and trade-offs. Create README.md with setup, run instructions, project structure, logs, test transcripts, and limitations. Add five test transcripts for the required behaviours.
