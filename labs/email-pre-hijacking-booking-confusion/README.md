# Lab 2 — Email Pre-Hijacking and Booking Confusion

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py
```

Open http://127.0.0.1:5001

## Vulnerable workflow

1. Register with `victim@example.test`.
2. Leave the email unverified.
3. Create a booking using that email.
4. The booking is attached to the currently authenticated account.

## Patched workflow

Enable Patched Mode and repeat the test. Booking requires a verified account email.

The lab uses synthetic data only.
