from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import secrets

app = Flask(__name__)
app.secret_key = "local-email-booking-lab-secret"
CORS(app, supports_credentials=True)

DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "lab.db"))
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
PATCHED_MODE = False


def db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email_verified INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        guest_name TEXT NOT NULL,
        email TEXT NOT NULL,
        hotel TEXT NOT NULL,
        room TEXT NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT NOT NULL,
        reference TEXT UNIQUE NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()


def get_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None

    conn = db()
    row = conn.execute(
        "SELECT id, email, email_verified FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.post("/api/register")
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify(error="Email and password are required"), 400

    conn = db()
    try:
        cur = conn.execute(
            "INSERT INTO users(email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify(error="That email is already registered"), 409

    conn.close()
    session["user_id"] = user_id
    return jsonify(message="Account created; email is unverified"), 201


@app.post("/api/login")
def login():
    data = request.get_json() or {}
    conn = db()
    user = conn.execute(
        "SELECT id FROM users WHERE email = ? AND password = ?",
        (data.get("email", "").strip().lower(), data.get("password", ""))
    ).fetchone()
    conn.close()

    if user is None:
        return jsonify(error="Invalid credentials"), 401

    session["user_id"] = user["id"]
    return jsonify(message="Logged in")


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(message="Logged out")


@app.get("/api/me")
def me():
    user = get_user()
    if user is None:
        return jsonify(error="Unauthorized"), 401

    return jsonify(user=user, patched_mode=PATCHED_MODE)


@app.post("/api/verify-email")
def verify_email():
    user = get_user()
    if user is None:
        return jsonify(error="Unauthorized"), 401

    conn = db()
    conn.execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user["id"],))
    conn.commit()
    conn.close()
    return jsonify(message="Synthetic email verified")


@app.get("/api/bookings")
def bookings():
    user = get_user()
    if user is None:
        return jsonify(error="Unauthorized"), 401

    conn = db()
    rows = conn.execute(
        """SELECT guest_name, email, hotel, room, check_in, check_out, reference
           FROM bookings WHERE user_id = ? ORDER BY id DESC""",
        (user["id"],)
    ).fetchall()
    conn.close()
    return jsonify(bookings=[dict(row) for row in rows])


@app.post("/api/bookings")
def create_booking():
    user = get_user()
    if user is None:
        return jsonify(error="Unauthorized"), 401

    data = request.get_json() or {}
    fields = ["guest_name", "email", "hotel", "room", "check_in", "check_out"]
    if any(not str(data.get(field, "")).strip() for field in fields):
        return jsonify(error="All booking fields are required"), 400

    booking_email = data["email"].strip().lower()

    if PATCHED_MODE:
        if not user["email_verified"]:
            return jsonify(error="Verify the account email before booking"), 403
        if booking_email != user["email"].lower():
            return jsonify(error="Booking email must match the verified account"), 403

    reference = "LAB-" + secrets.token_hex(4).upper()
    conn = db()
    conn.execute(
        """INSERT INTO bookings
           (user_id, guest_name, email, hotel, room, check_in, check_out, reference)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user["id"], data["guest_name"], booking_email, data["hotel"],
            data["room"], data["check_in"], data["check_out"], reference
        )
    )
    conn.commit()
    conn.close()

    return jsonify(message="Booking created", reference=reference), 201


@app.post("/api/lab/mode")
def mode():
    global PATCHED_MODE
    PATCHED_MODE = bool((request.get_json() or {}).get("patched_mode", False))
    return jsonify(patched_mode=PATCHED_MODE)


@app.post("/api/lab/reset")
def reset():
    global PATCHED_MODE
    conn = db()
    conn.execute("DELETE FROM bookings")
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    session.clear()
    PATCHED_MODE = False
    return jsonify(message="Lab reset")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=False)
