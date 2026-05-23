# Prompt Design

## System Prompt

```text
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
```

## Reasoning for Key Design Choices

The prompt is designed for a customer support workflow where reliability is more important than creativity. The assistant is explicitly restricted to the SOP so that it does not invent clinic policies, prices, or medical advice. The JSON output format makes the model response easier to validate in code and supports downstream workflow steps such as escalation logging, lead qualification, and summary generation.

## OpenAI API Usage

When `OPENAI_API_KEY` is set, the app uses the OpenAI Python SDK to generate SOP-grounded FAQ responses and final conversation summaries. The model is selected with `OPENAI_MODEL`, defaulting to `gpt-4o-mini`.

The OpenAI path uses the same strict SOP boundary as the system prompt: answer only from the provided SOP, do not guess missing information, and return escalation flags and reasons when escalation is needed.

## Hallucination Prevention

The assistant is instructed to answer only from the SOP data. If the answer is not available in the SOP, it must acknowledge the gap and escalate. This prevents the model from guessing missing details such as exact treatment suitability, discounts, availability, medical risks, or custom pricing.

The code also applies a second safety layer. If the response has low confidence, is out of scope, or matches escalation keywords, the workflow flags escalation even if the model response itself fails to do so.

If no API key is configured, or if an API call fails, the code uses a deterministic fallback mode. This fallback is intended for demo/testing reliability and keeps the CLI runnable without external API access.

## Confidence-Based Escalation

The workflow uses a confidence threshold of `0.65`. Any response below this threshold is treated as low confidence and escalated. The model is asked to return a `confidence` value, but the workflow does not rely only on the model. It also checks for:

- out-of-scope questions
- angry or frustrated sentiment
- explicit human-agent requests
- medical questions
- pricing negotiation
- more than two unanswered questions

Escalation reasons are stored in `logs/conversation_log.jsonl`.

## Tone and Persona

The tone is warm, concise, and professional. This is suitable for SMB customer support because customers usually want quick, clear answers rather than long explanations. The assistant avoids robotic wording but also avoids overpromising.

## Trade-Offs

This prototype uses both LLM prompting and deterministic keyword-based checks. The benefit is reliability and easier testing. The limitation is that keyword detection may miss subtle sentiment or unusual wording. In production, this could be improved using a dedicated sentiment classifier, better retrieval over SOP documents, and human feedback loops.
