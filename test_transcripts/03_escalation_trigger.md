# Test Transcript 03 - Escalation Trigger

Expected assignment behaviour: complaint or angry sentiment escalation.

Note: In OpenAI mode, wording may vary slightly, but the escalation reasons should include angry or frustrated sentiment.

```text
Closira Demo Assistant - Bloom Aesthetics Clinic
Type 'summary' to end the session and generate a structured summary.

Customer: I am very angry. My appointment was cancelled and nobody helped me.
AI: I am sorry this has been frustrating. I will hand this over to a human team member so you get the right support.
--------------------------------------------------
Escalation Triggered
Reason(s):
- angry_or_frustrated_sentiment
- low_confidence_or_out_of_scope
--------------------------------------------------
```

Expected behaviour:

- AI acknowledges the customer's frustration.
- AI does not argue or continue trying to solve an escalated complaint.
- AI triggers escalation with clear reason labels.
