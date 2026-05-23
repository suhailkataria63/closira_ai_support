# Test Transcript 05 — Conversation Summary

**Customer:** What are your filler prices?

**AI:** Fillers start from £250 at Bloom Aesthetics Clinic.

**AI Qualification Question:** Which service are you interested in: Botox, fillers, or consultation?

**Customer:** Fillers

**Customer:** summary

**Expected Structured Summary:**

```json
{
  "customer_intent": "Asked about filler service/pricing",
  "key_details_collected": {
    "Which service are you interested in: Botox, fillers, or consultation?": "Fillers"
  },
  "sop_gaps_identified": [],
  "escalation_reasons": [],
  "recommended_next_action": "Proceed with booking guidance through WhatsApp or website."
}
```

**Expected Behaviour:**

- Summary includes customer intent.
- Summary includes collected lead details.
- Summary identifies SOP gaps if any.
- Summary recommends the next action.
