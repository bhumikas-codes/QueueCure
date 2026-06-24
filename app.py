from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
import sqlite3
import time

app = Flask(__name__)
app.secret_key = "queuecure2026"
socketio = SocketIO(app, cors_allowed_origins="*")

RECEPTIONIST_USERNAME = "demo"
RECEPTIONIST_PASSWORD = "demo123"

DB_NAME = "queuecure.db"

# ── Database setup ──
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            name TEXT,
            status TEXT DEFAULT 'waiting',
            start_time REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            current_token INTEGER DEFAULT 0,
            avg_time REAL DEFAULT 10
        )
    """)
    cursor.execute("SELECT * FROM settings WHERE id=1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO settings VALUES (1, 0, 10)")
    conn.commit()
    conn.close()

init_db()

# ── Get current queue state ──
def get_queue_state():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE id=1")
    settings = cursor.fetchone()
    cursor.execute("SELECT * FROM patients ORDER BY token")
    patients = cursor.fetchall()
    conn.close()
    return {
        "current_token": settings["current_token"],
        "avg_time": settings["avg_time"],
        "total_tokens": len(patients),
        "patients": [dict(p) for p in patients]
    }

# ── Routes ──
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == RECEPTIONIST_USERNAME and password == RECEPTIONIST_PASSWORD:
            session["logged_in"] = True
            return redirect("/receptionist")
        return render_template("login.html", error="Invalid credentials!")
    return render_template("login.html")

@app.route("/receptionist")
def receptionist():
    if not session.get("logged_in"):
        return redirect("/login")
    return render_template("receptionist.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/patient")
def patient():
    return render_template("patient.html")

# ── SocketIO events ──
@socketio.on("connect")
def handle_connect():
    emit("queue_update", get_queue_state())

@socketio.on("add_patient")
def add_patient(data):
    name = data.get("name", "Patient")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM patients")
    count = cursor.fetchone()["cnt"]
    token = count + 1
    cursor.execute(
        "INSERT INTO patients (token, name, status) VALUES (?, ?, ?)",
        (token, name, "waiting")
    )
    conn.commit()
    conn.close()
    emit("queue_update", get_queue_state(), broadcast=True)

@socketio.on("call_next")
def call_next():
    state = get_queue_state()

    # Nothing to call
    if state["current_token"] >= state["total_tokens"]:
        return

    conn = get_connection()
    cursor = conn.cursor()

    next_token = state["current_token"] + 1

    # Record start time for new patient
    cursor.execute(
        "UPDATE patients SET start_time=? WHERE token=?",
        (time.time(), next_token)
    )

    # Calculate avg from previous patient if exists
    if state["current_token"] > 0:
        cursor.execute(
            "SELECT start_time FROM patients WHERE token=?",
            (state["current_token"],)
        )
        prev = cursor.fetchone()
        if prev and prev["start_time"]:
            elapsed = (time.time() - prev["start_time"]) / 60
            if elapsed >= 0.1:  # at least 6 seconds
                # Get all recorded times
                cursor.execute(
                    "SELECT start_time FROM patients WHERE start_time IS NOT NULL AND token < ?",
                    (next_token,)
                )
                times = cursor.fetchall()
                if len(times) >= 2:
                    diffs = []
                    time_list = [t["start_time"] for t in times]
                    for i in range(1, len(time_list)):
                        diff = (time_list[i] - time_list[i-1]) / 60
                        if diff >= 0.1:
                            diffs.append(diff)
                    if diffs:
                        new_avg = round(sum(diffs) / len(diffs), 1)
                        cursor.execute(
                            "UPDATE settings SET avg_time=? WHERE id=1",
                            (new_avg,)
                        )

    # Update current token
    cursor.execute(
        "UPDATE settings SET current_token=? WHERE id=1",
        (next_token,)
    )

    # Mark previous as served
    if state["current_token"] > 0:
        cursor.execute(
            "UPDATE patients SET status='served' WHERE token=?",
            (state["current_token"],)
        )

    # Mark new current as serving
    cursor.execute(
        "UPDATE patients SET status='serving' WHERE token=?",
        (next_token,)
    )

    conn.commit()
    conn.close()

    emit("queue_update", get_queue_state(), broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)