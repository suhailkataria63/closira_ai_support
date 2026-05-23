# Test Transcript 01 - In-SOP Question

Expected assignment behaviour: SOP grounded answering.

Note: In OpenAI mode, wording may vary slightly, but the answer should remain grounded in `data/sop.json`.

```text
Closira Demo Assistant - Bloom Aesthetics Clinic
Type 'summary' to end the session and generate a structured summary.

Customer: What are your Botox prices?
AI: Botox starts from £200 at Bloom Aesthetics Clinic.
To help you better, may I ask:
- Which service are you interested in: Botox, fillers, or consultation?
Customer: Botox
```

Expected behaviour:

- AI answers from the SOP only.
- AI does not invent a final treatment price.
- AI asks the first lead qualification question naturally.
- No escalation is required.
