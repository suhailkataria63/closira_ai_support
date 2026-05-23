# Test Transcript 04 - Lead Qualification

Expected assignment behaviour: structured lead qualification.

Note: In OpenAI mode, wording may vary slightly. This transcript avoids inventing unsupported fields: the current SOP supports interested service, previous visit status, and preferred booking channel.

```text
Closira Demo Assistant - Bloom Aesthetics Clinic
Type 'summary' to end the session and generate a structured summary.

Customer: I want to book an appointment.
AI: Bookings can be made via WhatsApp or the website.
To help you better, may I ask:
- Which service are you interested in: Botox, fillers, or consultation?
Customer: Fillers

Customer: What are your opening hours?
AI: Bloom Aesthetics Clinic is open Monday to Saturday, 9 am to 7 pm.
To help you better, may I ask:
- Have you visited Bloom Aesthetics Clinic before?
Customer: No, this will be my first visit.

Customer: Can I book online?
AI: Bookings can be made via WhatsApp or the website.
To help you better, may I ask:
- Would you prefer booking through WhatsApp or the website?
Customer: WhatsApp
```

Expected qualification details collected:

- Interested service: Fillers
- Previous visit status: No, this will be my first visit.
- Preferred booking channel: WhatsApp

Current limitation:

- The current CLI does not ask for business type, customer type, team size, or current tools because those fields are not part of the current Bloom Aesthetics Clinic SOP.
