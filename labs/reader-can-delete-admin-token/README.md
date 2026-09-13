# Reader Can Delete Admin API Token

A deliberately vulnerable web application demonstrating **Broken Object Level Authorization (BOLA/IDOR)** against security-sensitive API token objects.

The lab simulates a SaaS application where a low-privileged Reader can manipulate an Admin's API token by directly addressing the Admin token's object ID.

## What This Lab Demonstrates

The intended vulnerability is:

> A Reader can delete an Admin's API token because the token deletion endpoint verifies that the caller belongs to the same organization but fails to verify whether the caller is authorized to perform the operation against the target token.

The normal application interface does not provide the Reader with a token-deletion function.

The vulnerable API must therefore be discovered and tested through HTTP/API reconnaissance, such as Burp Suite.

### Vulnerable endpoint

```http
DELETE /api/v2/tokens/{token_id}
```

A successful unauthorized deletion returns:

```http
HTTP/1.1 204 No Content
```

## Requirements

### Required

* Linux, WSL, or another Unix-like environment
* Python 3.10+
* Python virtual environment support
* A modern web browser

### Recommended

* Burp Suite Community or Professional
* Burp's browser or another browser configured to use Burp Proxy

No external database server is required.

The application uses SQLite.

## Installation

Clone the repository:

```bash
git clone https://github.com/sarumaan/security-research.git
```

Enter the lab:

```bash
cd security-research/labs/reader-can-delete-admin-token
```

Create the Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r backend/requirements.txt
```

## Run the Lab

Start the Flask application:

```bash
python backend/app.py
```

The application will run on:

```text
http://127.0.0.1:5000
```

If the application is running inside WSL and accessed from Windows, use the WSL-accessible address provided by your environment.

Open the application in a browser.

## Default Credentials

### Reader

```text
Email:    bob.reader@example.test
Password: ReaderPass123!
Role:     reader
```

### Admin

```text
Email:    alice.admin@example.test
Password: AdminPass123!
Role:     admin
```

These credentials are intentionally included because this is a local security training laboratory.

## Lab Interface

The application provides a normal SaaS-style interface for:

* Authentication
* Dashboard access
* Account information
* API token information
* Session testing
* Lab reset

The Reader interface does **not** provide a token deletion button.

This is intentional.

The objective is to discover and interact with the underlying API rather than simply clicking a vulnerability-specific UI control.

## Intended Attack Flow

The recommended workflow is:

### 1. Reset the Lab

Use **Reset Lab** to restore the original state.

This recreates:

* Admin account
* Reader account
* Admin API token
* Reader API token

### 2. Log in as Reader

Use:

```text
bob.reader@example.test
ReaderPass123!
```

### 3. Intercept application traffic

Configure the browser to use Burp Suite and interact with the application normally.

Look for token-related API requests.

### 4. Investigate the API

The application exposes token-related API functionality.

The relevant object is an API token belonging to a user in the same organization.

The objective is to determine whether the server properly enforces authorization when a token object is addressed directly by ID.

### 5. Identify the Admin token object

Determine the Admin token's object ID through API reconnaissance.

Do not rely on the normal Reader UI displaying the Admin token.

### 6. Test the deletion operation

Send:

```http
DELETE /api/v2/tokens/{admin_token_id}
```

using the authenticated Reader session.

The vulnerable application incorrectly permits the operation.

Expected response:

```http
HTTP/1.1 204 No Content
```

### 7. Verify the impact

The Admin token should no longer exist.

The Admin's token-dependent session/API access should become invalid.

### 8. Reset the Lab

Use **Reset Lab** to restore the original state.

After resetting, both accounts and their tokens should work again.

## Vulnerable Behavior

The vulnerable authorization model effectively checks:

```text
Is the caller authenticated?
        ↓
Is the target token in the same organization?
        ↓
YES → allow deletion
```

It does not sufficiently enforce:

```text
Is this caller authorized to delete this specific token?
```

This creates a broken object-level authorization condition.

## Expected Security Model

A secure implementation should verify the caller's authorization against the target object before allowing deletion.

Conceptually:

```text
Authenticated caller
        ↓
Identify target token
        ↓
Verify organization ownership
        ↓
Verify caller's authorization for target
        ↓
Allow or deny operation
```

A Reader should not be able to delete an Admin's security token merely because both accounts belong to the same organization.

## Resetting the Lab

The Reset Lab function restores the initial database state.

It recreates:

```text
Organization
├── Admin
│   └── Admin API Token
│
└── Reader
    └── Reader API Token
```

Use Reset Lab whenever you want to repeat the attack from a clean state.

## Burp Suite

Burp Suite is recommended for this lab because the vulnerability requires direct interaction with an API endpoint that is not exposed as a deletion control in the normal Reader interface.

A typical workflow is:

```text
Browser
   ↓
Burp Proxy
   ↓
Flask Application
   ↓
SQLite
```

Burp can be used to:

* Inspect requests
* Identify API endpoints
* Examine object identifiers
* Send requests to Repeater
* Modify HTTP methods and paths
* Observe authorization behavior
* Verify the `204 No Content` response

## Project Structure

```text
reader-can-delete-admin-token/
├── README.md
├── docker-compose.yml
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
└── data/
    └── lab.db
```

The SQLite database is generated locally and should not be treated as production data.

## Technology Stack

* Python
* Flask
* Flask-CORS
* SQLite
* HTML
* CSS
* JavaScript

## Learning Objectives

This lab is designed to teach the following concepts:

* Broken Object Level Authorization
* IDOR/BOLA testing
* Object ownership
* Authorization versus authentication
* Privilege boundaries
* API reconnaissance
* Hidden API functionality
* Security-sensitive object manipulation
* Destructive API operations
* Verifying impact after an unauthorized operation

## Safety

This application is intentionally vulnerable.

Run it only in a controlled environment that you own or are authorized to test.

Do not expose the vulnerable application to the public Internet.

The credentials and tokens included in this README are **local laboratory credentials** and must not be reused for real systems.

## Vulnerability Classification

Primary classification:

**OWASP API1:2023 — Broken Object Level Authorization**

Related concepts:

* IDOR
* Access-control failure
* Unauthorized object modification/deletion
* Privilege boundary violation
* Security-token lifecycle manipulation
