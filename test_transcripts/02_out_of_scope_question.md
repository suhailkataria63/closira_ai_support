# Test Transcript 02 - Out-of-Scope Question

Expected assignment behaviour: SOP gap detection and escalation.

Note: In OpenAI mode, wording may vary slightly, but the assistant should not claim that laser hair removal is offered because it is not present in the SOP.

```text
Closira Demo Assistant - Bloom Aesthetics Clinic
Type 'summary' to end the session and generate a structured summary.

Customer: Do you offer laser hair removal?
AI: I do not have that detail in the clinic SOP, so I will pass this to a human team member.
--------------------------------------------------
Escalation Triggered
Reason(s):
- low_confidence_or_out_of_scope
--------------------------------------------------
```

Expected behaviour:

- AI does not guess unsupported services.
- AI clearly identifies that the information is not in the SOP.
- AI escalates to a human using the polished escalation block.
