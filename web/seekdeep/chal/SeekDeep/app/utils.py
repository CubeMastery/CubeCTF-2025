import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access that page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_username_hash(username):
    return int(hashlib.sha256(username.encode()).hexdigest(), 16)