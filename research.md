---
layout: default
title: Research
permalink: /research/
---

# Security Research

This section contains sanitized case studies documenting real
application-security findings from my previous engagements.

---
## Case Studies
---
### Reader Access level Can Delete Admin Access Token

**Vulnerability:** Broken Object Level Authorization (BOLA / IDOR)  
**Status:** Validated

A reader-level access token could delete an administrator-level token
record by changing the object identifier in the API request.

[Read the case study](case-studies/reader-can-delete-admin-token/index.md)

---

### Email Pre-Hijacking Causes Booking and Account Confusion

**Vulnerability:** Account Pre-Hijacking / Identity Confusion / Business Logic  
**Status:** Validated and Paid

An attacker could attach an unverified email address to an existing
account and cause a subsequent booking made with that email to become
associated with the attacker's account, exposing booking information
and personal data.

[Read the case study](case-studies/email-pre-hijacking-booking-account-confusion/index.md)

---

### Sign-In Link Injection Enables Account Takeover

**Vulnerability:** Authentication Token Leakage / Account Takeover  
**Status:** Validated — Duplicate

An attacker-controlled `siteUrl` was accepted by the customer sign-in-link
function. The resulting legitimate sign-in email contained an
attacker-controlled URL with a live authentication token.

The token was captured using Burp Collaborator, demonstrating
authentication token disclosure and a direct account takeover path.

[Read the case study](case-studies/sign-in-link-injection-token-leakage/index.md)

---

### Non-Admin Member Can Invite Users Into Premium Organization

**Vulnerability:** Broken Function Level Authorization / BOLA  
**Status:** Validated — Duplicate

A non-admin organization member could modify the `organizationId` in the
member invitation request and invite users into another organization.

The server accepted the unauthorized request, returned `201 Created`,
and delivered the invitation to the target user. After accepting the
invitation, the user became a member of the target organization.

[Read the case study](case-studies/non-admin-member-invites-premium-organization/index.md)

---

### API Key Exposure Leads to Unauthorized PII and Financial Data Access

**Vulnerability:** Unauthenticated Database Access / Sensitive Data Exposure  
**Status:** Validated and Paid

A publicly exposed Firebase configuration allowed the associated
Realtime Database to be identified. The database permitted
unauthenticated access to sensitive user information, including names,
email addresses, user identifiers, room numbers, dates, and financial
data.

[Read the case study](case-studies/firebase-pii-exposure/index.md)
