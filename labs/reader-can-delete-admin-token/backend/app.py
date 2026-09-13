from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "reader-delete-admin-token-lab-secret"

CORS(app, supports_credentials=True)

DATABASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "lab.db")
)
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            FOREIGN KEY (organization_id)
                REFERENCES organizations(id)
        );

        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        );
    """)

    existing_org = conn.execute(
        "SELECT id FROM organizations LIMIT 1"
    ).fetchone()

    if existing_org is None:
        cursor = conn.execute(
            "INSERT INTO organizations (name) VALUES (?)",
            ("Acme Corporation",)
        )

        organization_id = cursor.lastrowid

        cursor = conn.execute(
            """
            INSERT INTO users
            (organization_id, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (
            organization_id,
            "alice.admin@example.test",
            "AdminPass123!",
            "admin"
            )
        )

        admin_id = cursor.lastrowid

        cursor = conn.execute(
            """
            INSERT INTO users
            (organization_id, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (
            organization_id,
            "bob.reader@example.test",
            "ReaderPass123!",
            "reader")
        )

        reader_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO tokens
            (user_id, token, name)
            VALUES (?, ?, ?)
            """,
            (
                admin_id,
                "lab-admin-token-001",
                "Admin API Token"
            )
        )

        conn.execute(
            """
            INSERT INTO tokens
            (user_id, token, name)
            VALUES (?, ?, ?)
            """,
            (
                reader_id,
                "lab-reader-token-001",
                "Reader API Token"
            )
        )

        conn.commit()

    conn.close()


def authenticate():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    conn = get_db()

    row = conn.execute(
        """
        SELECT
            users.id AS user_id,
            users.email,
            users.role,
            organizations.id AS organization_id,
            organizations.name AS organization_name,
            tokens.id AS token_id,
            tokens.token AS token
        FROM users
        JOIN organizations
            ON organizations.id = users.organization_id
        LEFT JOIN tokens
            ON tokens.user_id = users.id
        WHERE users.id = ?
        ORDER BY tokens.id
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    # The account's API token must still exist.
    if row["token_id"] is None:
        session.clear()
        return None

    return dict(row)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email", "")
    password = data.get("password", "")

    conn = get_db()

    user = conn.execute(
        """
        SELECT
            users.id,
            users.organization_id,
            users.email,
            users.role,
            tokens.id AS token_id
        FROM users
        LEFT JOIN tokens
            ON tokens.user_id = users.id
        WHERE users.email = ?
        AND users.password = ?
        """,
        (email, password)
    ).fetchone()

    conn.close()

    if user is None or user["token_id"] is None:
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["id"]

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    })

@app.route("/")
def frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def frontend_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/api/v2/me", methods=["GET"])
def current_user():
    caller = authenticate()

    if caller is None:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "authenticated": True,
        "user": {
            "id": caller["user_id"],
            "email": caller["email"],
            "role": caller["role"]
        },
        "organization": {
            "id": caller["organization_id"],
            "name": caller["organization_name"]
        }
    })

@app.route("/api/v2/me/token", methods=["GET"])
def current_token():
    caller = authenticate()

    if caller is None:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()

    token = conn.execute(
        """
        SELECT
            tokens.id,
            tokens.name,
            users.email,
            users.role
        FROM tokens
        JOIN users
            ON users.id = tokens.user_id
        WHERE tokens.user_id = ?
        ORDER BY tokens.id
        LIMIT 1
        """,
        (caller["user_id"],)
    ).fetchone()

    conn.close()

    if token is None:
        return jsonify({"error": "Token not found"}), 404

    return jsonify(dict(token))

@app.route("/api/v2/tokens", methods=["GET"])
def list_tokens():
    caller = authenticate()

    if caller is None:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            tokens.id,
            tokens.name,
            tokens.token,
            users.email,
            users.role
        FROM tokens
        JOIN users
            ON users.id = tokens.user_id
        WHERE users.organization_id = ?
        ORDER BY tokens.id
        """,
        (caller["organization_id"],)
    ).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])
@app.route("/api/v2/tokens/<int:token_id>", methods=["DELETE"])
def delete_token(token_id):
    caller = authenticate()

    if caller is None:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    conn = get_db()

    target = conn.execute(
        """
        SELECT
            tokens.id,
            tokens.name,
            tokens.user_id,
            users.email,
            users.role,
            users.organization_id
        FROM tokens
        JOIN users
            ON users.id = tokens.user_id
        WHERE tokens.id = ?
        """,
        (token_id,)
    ).fetchone()

    if target is None:
        conn.close()

        return jsonify({
            "error": "Token not found"
        }), 404

    # INTENTIONALLY VULNERABLE
    #
    # The application checks that the caller is authenticated
    # and belongs to the organization, but does NOT verify
    # whether the caller is authorized to delete the target token.
    #
    # This reproduces the BOLA/IDOR vulnerability.

    if target["organization_id"] != caller["organization_id"]:
        conn.close()

        return jsonify({
            "error": "Forbidden"
        }), 403
    # if target["user_id"] != caller["user_id"] and caller["role"] != "admin":
    #     conn.close()
    #     return jsonify({
    #         "error": "Forbidden"
    #     }), 403
    
    conn.execute(
        "DELETE FROM tokens WHERE id = ?",
        (token_id,)
    )

    conn.commit()
    conn.close()

    return "", 204
@app.route("/api/lab/reset", methods=["POST"])
def reset_lab():
    conn = get_db()

    # Remove all current lab data.
    conn.execute("DELETE FROM tokens")
    conn.execute("DELETE FROM users")
    conn.execute("DELETE FROM organizations")

    # Recreate organization.
    cursor = conn.execute(
        "INSERT INTO organizations (name) VALUES (?)",
        ("Acme Corporation",)
    )

    organization_id = cursor.lastrowid

    # Recreate Admin.
    cursor = conn.execute(
        """
        INSERT INTO users
        (organization_id, email, password, role)
        VALUES (?, ?, ?, ?)
        """,
        (
        organization_id,
        "alice.admin@example.test",
        "AdminPass123!",
        "admin"
        )
    )

    admin_id = cursor.lastrowid

    # Recreate Reader.
    cursor = conn.execute(
        """
        INSERT INTO users
        (organization_id, email, password, role)
        VALUES (?, ?, ?, ?)
        """,
        (
            organization_id,
            "bob.reader@example.test",
            "ReaderPass123!",
            "reader"
        )
    )
    

    reader_id = cursor.lastrowid

    # Recreate Admin token.
    conn.execute(
        """
        INSERT INTO tokens
        (user_id, token, name)
        VALUES (?, ?, ?)
        """,
        (
            admin_id,
            "lab-admin-token-001",
            "Admin API Token"
        )
    )

    # Recreate Reader token.
    conn.execute(
        """
        INSERT INTO tokens
        (user_id, token, name)
        VALUES (?, ?, ?)
        """,
        (
            reader_id,
            "lab-reader-token-001",
            "Reader API Token"
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "reset",
        "message": "Lab restored to its initial state."
    })

if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
