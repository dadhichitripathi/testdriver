# Risk and Escalation Matrix

Use this matrix to prevent operational failures and respond quickly when issues happen.

## 1) Severity levels

| Severity | Definition | First Response | Resolution Target |
|---|---|---|---|
| P0 Critical | Fraud campaign, mass misinformation, security risk | <= 15 minutes | <= 2 hours |
| P1 High | Incentive miscommunication, payout panic, abuse spike | <= 30 minutes | <= 6 hours |
| P2 Medium | Delayed helpdesk response, repeat confusion topics | <= 2 hours | <= 24 hours |
| P3 Low | Minor wording errors, cosmetic content issues | <= 24 hours | <= 3 days |

## 2) Common risk scenarios and playbook

### Scenario A: Fake incentive screenshot spreading

- **Trigger:** Same fake message appears in 2+ groups.
- **Immediate actions:**
  1. Remove offending messages.
  2. Broadcast anti-fake clarification in Channel and Announcement group.
  3. Temporarily switch high-noise group to admin-only if needed.
- **Owner:** Community Lead.
- **Escalation:** Operations Manager for official correction card.

### Scenario B: Fraud/UPI request impersonating support

- **Trigger:** Any OTP/UPI/password request reported.
- **Immediate actions:**
  1. Remove user instantly (no 3-strike for fraud).
  2. Send safety broadcast in all groups.
  3. Log incident with screenshot and user handle.
- **Owner:** Moderator on shift.
- **Escalation:** Security contact + Community Lead.

### Scenario C: Payout-related panic in group

- **Trigger:** 10+ similar complaints in 2 hours.
- **Immediate actions:**
  1. Post acknowledgment and expected update time.
  2. Move detailed ticket collection to Helpdesk.
  3. Share standardized intake format.
- **Owner:** Helpdesk Lead.
- **Escalation:** Payments/Support SPOC.

### Scenario D: Helpdesk SLA breach (>120 min FRT)

- **Trigger:** Backlog crosses SLA target.
- **Immediate actions:**
  1. Activate backup responder.
  2. Tag unresolved queries by severity.
  3. Close low-complexity tickets first.
- **Owner:** Helpdesk Lead.
- **Escalation:** Community Lead for temporary manpower shift.

### Scenario E: Abuse/harassment in community group

- **Trigger:** Any repeated abuse or threatening language.
- **Immediate actions:**
  1. Remove message.
  2. Issue warning or immediate removal based on severity.
  3. Lock thread if escalation continues.
- **Owner:** Moderator.
- **Escalation:** Community Lead for permanent ban decision.

## 3) Escalation ladder

1. **L1:** Shift Moderator / Helpdesk Agent
2. **L2:** Community Lead
3. **L3:** Operations Manager
4. **L4:** Security/Payments/App specialist SPOCs

Keep a single source of truth list with names, phone numbers, and backups.

## 4) Mandatory incident log fields

- Incident ID
- Date/time detected
- Severity (P0-P3)
- Source group/channel
- Summary
- Action taken
- Owner
- Escalated to
- Resolved time
- Prevention note

## 5) Post-incident review template

- What happened?
- Why it happened?
- How fast we detected it?
- Did we meet SLA?
- What process change prevents recurrence?

Run P0/P1 reviews within 24 hours.
