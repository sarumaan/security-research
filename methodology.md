---
layout: default
title: Methodology
permalink: /methodology/
---

# Methodology

My approach to application security research is based on understanding
the security model of an application and then testing whether the
backend actually enforces that model.

---

## 1. Identity

First, establish who is making the request.

Questions include:

- Which account is authenticated?
- What identity does the server associate with the request?
- Can identity be changed, confused, or represented in another form?

---

## 2. Authorization

Determine what the authenticated identity is allowed to do.

I compare behavior between:

- Different users
- Different roles
- Different privileges
- Different tenants
- Authenticated and unauthenticated states

---

## 3. Ownership

Identify which user, organization, or tenant owns each object.

Then test whether an identity can:

- Read another user's object
- Modify another user's object
- Delete another user's object
- Perform actions on objects outside its ownership boundary

---

## 4. Relationships

Applications often authorize access through relationships rather than
direct ownership.

Examples include:

text
User → Organization
User → Team
User → Project
User → Invitation
User → Position
User → Resource

I test whether changing or bypassing these relationships changes what
the application allows the user to access.

---

## 5. Privilege Transitions

I test what happens when privileges change.

For example:
```text
Admin
  ↓
Member
  ↓
No Access
```
The important question is whether previously granted capabilities are actually removed when the user's privilege changes.

---

## 6. State Transitions

Many vulnerabilities appear when an object moves between states.

Examples:
```text
Pending → Active
Active → Disabled
Member → Removed
Draft → Published
Invitation → Accepted
```
I test whether operations that should only be possible in one state
remain available after a transition.

---

## 7. Workflow

I examine whether application workflows enforce the intended sequence.

For example:
```text
Create
   ↓
Approve
   ↓
Execute
   ↓
Complete
```
I test whether steps can be skipped, reordered, repeated, or performed
by an unauthorized identity.

---

## 8. GraphQL

For GraphQL applications, I examine:
```text
Queries
Mutations
Arguments
Object identifiers
Nested relationships
Fragments
Directives
Schema structure
Authorization boundaries
```
I pay particular attention to whether an object that cannot be accessed
directly becomes reachable through an authorized relationship.

I circumvent authorization boundaries through batch queries and aliasing.

---

## 9. Backend Enforcement

Finally, I compare the application's intended security model with what the backend actually enforces.

The central question is:

Does the server enforce the security boundary, or does it merely assume that the client will respect it?

Core Model

My research can be summarized as:
```text
Identity
   ↓
Authorization
   ↓
Ownership
   ↓
Relationships
   ↓
Privileges
   ↓
State
   ↓
Workflow
   ↓
Backend Enforcement
```

The goal is to identify where these boundaries break down.
