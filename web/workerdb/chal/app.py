from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from multiprocessing import Lock
from functools import wraps
import secrets
import sqlite3
import json
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

ALLOWED_ATTRIBUTES = {
    'role', 'email', 'display_name', 'theme', 'language', 'notifications',
    'timezone', 'avatar', 'bio', 'website', 'location'
}

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            attributes TEXT NOT NULL
        )
    ''')

    c.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        admin_attrs = json.dumps({
            'role': 'admin',
            'email': 'admin@example.com',
            'display_name': 'Administrator'
        })
        admin_password = secrets.token_hex(16)
        c.execute('INSERT INTO users (username, password, attributes) VALUES (?, ?, ?)',
                 ('admin', admin_password, admin_attrs))
        print("created admin account with password:", admin_password)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

l = Lock()
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        with l:
            return f(*args, **kwargs)
    return decorated

def has_xss(value):
    if not isinstance(value, str):
        return False
    return any(c in value for c in ['<', '>', '"', "'", '(', ')', '{', '}', '='])

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Invalid credentials"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            db.close()
            return jsonify({"error": "Username already exists"}), 400

        attributes = json.dumps({
            'role': 'user',
            'email': '',
            'display_name': username,
            'theme': 'light'
        })

        cursor.execute('INSERT INTO users (username, password, attributes) VALUES (?, ?, ?)',
                      (username, password, attributes))

        db.commit()
        db.close()
        return jsonify({"message": "Registration successful"})

    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Invalid credentials"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id, attributes FROM users WHERE username = ? AND password = ?',
                      (username, password))

        user = cursor.fetchone()
        db.close()

        if user:
            attrs = json.loads(user['attributes'])
            session['user_id'] = user['id']
            session['role'] = attrs.get('role')
            return jsonify({"message": "Login successful"})

        return jsonify({"error": "Invalid credentials"}), 401

    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500

@app.route('/api/settings/update', methods=['POST'])
@requires_auth
def update_settings():
    try:
        user_id = session['user_id']
        new_attrs = request.get_json()

        if not new_attrs:
            return jsonify({"error": "Invalid input"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT attributes FROM users WHERE id = ?', (user_id,))
        current_attrs = json.loads(cursor.fetchone()['attributes'])

        temp_attrs = current_attrs.copy()
        for key in new_attrs:
            if key in current_attrs:
                temp_attrs[key] = None

        cursor.execute('UPDATE users SET attributes = ? WHERE id = ?',
                    (json.dumps(temp_attrs), user_id))
        db.commit()

        sanitized_attrs = {}
        for key, value in new_attrs.items():
            if key in ALLOWED_ATTRIBUTES:
                if not has_xss(value):
                    sanitized_attrs[key] = value

        cursor.execute('SELECT attributes FROM users WHERE id = ?', (user_id,))
        current_attrs = json.loads(cursor.fetchone()['attributes'])

        final_attrs = current_attrs.copy()
        for key, value in sanitized_attrs.items():
            final_attrs[key] = value
        final_attrs['role'] = 'user'

        cursor.execute('UPDATE users SET attributes = ? WHERE id = ?',
                    (json.dumps(final_attrs), user_id))
        db.commit()
        db.close()

        return jsonify({"message": "Settings updated successfully"})

    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500

@app.route('/api/manage/permissions', methods=['POST'])
@requires_auth
def manage_permissions():
    try:
        user_id = session['user_id']
        data = request.get_json()

        if not data or 'target_user' not in data or 'new_role' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        target_username = data['target_user']
        new_role = data['new_role']

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT attributes FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        current_user_attrs = json.loads(user_data['attributes'])

        if current_user_attrs.get('role') != 'user':
            cursor.execute('SELECT id, attributes FROM users WHERE username = ?', (target_username,))
            target_user = cursor.fetchone()

            if not target_user:
                db.close()
                return jsonify({"error": "Target user not found"}), 404

            target_attrs = json.loads(target_user['attributes'])
            target_attrs['role'] = new_role

            cursor.execute('UPDATE users SET attributes = ? WHERE username = ?',
                       (json.dumps(target_attrs), target_username))

            db.commit()
            db.close()
            return jsonify({"message": "Permissions updated successfully"})

        db.close()
        return jsonify({"error": "Access denied"}), 403

    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500

@app.route('/api/admin', methods=['GET'])
@requires_auth
def admin_panel():
    try:
        user_id = session['user_id']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT attributes FROM users WHERE id = ?', (user_id,))

        user_data = cursor.fetchone()
        db.close()

        attrs = json.loads(user_data['attributes'])

        if attrs.get('role') == 'admin':
            return jsonify({
                "message": "Welcome to the admin panel",
                "flag": os.getenv("FLAG", "cube{example_flag}")
            })

        return jsonify({"error": "Access denied"}), 403

    except sqlite3.Error:
        return jsonify({"error": "Server error"}), 500

@app.get("/admin")
def admin():
    if session.get("user_id"):
        return render_template("admin.html")
    return redirect(url_for("index"))

@app.get("/login")
def login():
    return render_template("login.html")

@app.get("/register")
def register():
    return render_template("register.html")

@app.get("/")
def index():
    if session.get("user_id"):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT username, attributes FROM users WHERE id = ?',
                      (session["user_id"],))
        user = cursor.fetchone()
        db.close()
        return render_template("home.html", user=user[0], attributes=json.loads(user[1]), allowed_attrs=ALLOWED_ATTRIBUTES)
    return render_template("index.html")

init_db()
