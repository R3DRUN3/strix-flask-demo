
import os
import sqlite3
import subprocess

from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# VULNERABILITY: Hardcoded application secret
app.secret_key = "super-secret-demo-key-12345"

DATABASE = "demo.db"
FILES_DIRECTORY = "./files"


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute(
        "INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123')"
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return jsonify({
        "application": "Strix Vulnerable Flask Demo",
        "endpoints": [
            "/user?username=admin",
            "/hello?name=world",
            "/ping?host=127.0.0.1",
            "/files/<filename>"
        ]
    })


@app.route("/user")
def get_user():
    username = request.args.get("username", "")

    # VULNERABILITY: SQL Injection
    conn = sqlite3.connect(DATABASE)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = conn.execute(query).fetchall()
    conn.close()

    return jsonify(result)


@app.route("/hello")
def hello():
    name = request.args.get("name", "world")

    # VULNERABILITY: Reflected Cross-Site Scripting (XSS)
    return render_template_string(
        f"<h1>Hello {name}!</h1>"
    )


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")

    # VULNERABILITY: OS Command Injection
    result = subprocess.getoutput(f"ping -c 1 {host}")

    return f"<pre>{result}</pre>"


@app.route("/files/<path:filename>")
def download_file(filename):
    # VULNERABILITY: Path Traversal
    filepath = os.path.join(FILES_DIRECTORY, filename)

    with open(filepath, "r") as file:
        return file.read()


if __name__ == "__main__":
    init_db()

    # VULNERABILITY: Debug mode enabled
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
