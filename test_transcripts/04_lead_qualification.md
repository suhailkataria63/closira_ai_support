# Test Transcript 04 - Lead Qualification

Expected assignment behaviour: exactly three structured lead qualification questions.

Note: In OpenAI mode, wording of the SOP answer may vary slightly. The qualification questions are fixed by the workflow and should match this sequence.

```text
Closira Demo Assistant - Bloom Aesthetics Clinic
Type 'summary' to end the session and generate a structured summary.

Customer: What are your Botox prices?
AI: Botox starts from £200 at Bloom Aesthetics Clinic.
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

Expected qualification details collected:

- `interested_service`: Botox
- `previous_visit_status`: No
- `preferred_booking_channel`: WhatsApp

Current limitation:

- The workflow asks the three clinic-specific qualification questions from the SOP. It does not ask business type, team size, or current tools because those are not relevant to the Bloom Aesthetics Clinic SOP.
