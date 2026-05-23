# Test Transcript 05 - Conversation Summary

Expected assignment behaviour: structured final conversation summary.

Note: In OpenAI mode, wording may vary slightly, but the final summary should keep the same structured sections.

```text
Closira Demo Assistant - Bloom Aesthetics Clinic
Type 'summary' to end the session and generate a structured summary.

Customer: What are your Botox prices?
AI: Botox starts from £200 at Bloom Aesthetics Clinic.
To help you better, may I ask:
- Which service are you interested in: Botox, fillers, or consultation?
Customer: Botox

Customer: summary

--------------------------------------------------
Conversation Summary
--------------------------------------------------
Customer Intent:
Asked about Botox service/pricing

Key Details Collected:
- Interested service: Botox

SOP Gaps Identified:
- None

Escalation Reasons:
- None

Recommended Next Action:
Proceed with booking guidance through WhatsApp or website.
--------------------------------------------------
```

Expected behaviour:

- Summary includes the customer intent.
- Summary includes collected lead details.
- Summary lists SOP gaps as `None` when there were no unsupported questions.
- Summary lists escalation reasons as `None` when no escalation was triggered.
- Summary recommends the next action in a readable terminal format.
