# Prompt Design

## Full System Prompt

```text
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
```

## Design Rationale

The prompt is designed for reliability over creativity. Customer support for an SMB needs clear, bounded answers rather than broad model reasoning. The assistant is therefore instructed to answer only from the SOP, avoid unsupported claims, and return explicit flags that the workflow can validate.

The prompt also separates the AI response from workflow control. The model can propose an answer and escalation metadata, while the Python workflow still performs deterministic checks for low confidence, out-of-scope questions, complaint sentiment, medical topics, and human handoff requests.

## Hallucination Prevention

The main hallucination control is the SOP boundary: the assistant may only answer using `data/sop.json`. If a customer asks about something absent from the SOP, such as unsupported services, medical suitability, discounts, or custom pricing, the assistant should not guess.

The workflow adds a second layer of protection. Even if the model output is too confident, the code checks escalation rules independently and can still flag the conversation for a human.

## Confidence and Out-of-Scope Escalation

The workflow treats confidence below `0.65` as low confidence. Low-confidence answers and out-of-scope questions are escalated because the assistant should not continue when the SOP does not support the answer.

Out-of-scope examples include:

- services not listed in the SOP
- medical advice or treatment suitability
- unlisted prices or discounts
- policies not present in the SOP

## Tone and Persona

The assistant uses a friendly, concise, professional tone suitable for small business customer support. It should sound helpful and calm without overpromising. Responses should be short because customers usually want quick answers and a clear next step.

## Escalation Triggers

The workflow escalates for:

- out-of-scope or low-confidence answers
- angry sentiment or complaints
- medical questions
- pricing negotiation
- explicit human handoff requests
- more than two unanswered questions

Escalation reasons are returned as clear labels such as `low_confidence_or_out_of_scope`, `angry_or_frustrated_sentiment`, `medical_question`, `pricing_negotiation`, and `explicit_human_request`.

## Structured Output and Reliability

The OpenAI response is requested as JSON with clear fields:

- `answer`
- `confidence`
- `used_sop_fields`
- `out_of_scope`
- `escalation_required`
- `escalation_reason`
- `next_question`

This structure makes the response easier to validate, log, and pass into later workflow stages. It also keeps the four assignment stages explicit: FAQ answering, lead qualification, escalation detection, and conversation summary.

## OpenAI and Fallback Mode

When `OPENAI_API_KEY` is available, the app uses the OpenAI Python SDK for SOP-grounded FAQ answering and final summary generation. The model is selected with `OPENAI_MODEL`, defaulting to `gpt-4o-mini`.

If no API key is configured, the OpenAI package is unavailable, or an API call fails, the app uses deterministic fallback logic. This fallback mode supports safe testing and demos because the CLI remains runnable without external API access.
