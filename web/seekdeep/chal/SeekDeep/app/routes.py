from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response, json
from werkzeug.security import generate_password_hash, check_password_hash
import random
from . import app, db
from .models import User
from .utils import login_required, get_username_hash
from .consts import ASCEND_WORDS, SPIRITS, COLORS, RIDDLES

@app.route('/index.html')
def index():
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        head_size = request.form.get("head_size")
        head_size = float(head_size) if head_size else None
        is_bald = request.form.get("is_bald") == "on"
        eyesight = request.form.get("eyesight")
        largest_count = request.form.get("largest_count")
        favorite_vegetable = request.form.get("favorite_vegetable")
        cosmic_color = request.form.get("cosmic_color")
        left_shoes = request.form.get("left_shoes")
        left_shoes = int(left_shoes) if left_shoes else None
        mythical_creature = request.form.get("mythical_creature")

        if not username or not password:
            flash("Username and password are required!")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        user = User(
            username=username, password=hashed_password,
            head_size=head_size, is_bald=is_bald, eyesight=eyesight,
            largest_count=largest_count, favorite_vegetable=favorite_vegetable,
            cosmic_color=cosmic_color, left_shoes=left_shoes, mythical_creature=mythical_creature
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))
        except Exception:
            db.session.rollback()
            flash("Username already exists!")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!")
            return redirect(url_for("ascend"))
        flash("Invalid credentials!")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("home"))

@app.route('/ascend')
@login_required
def ascend():
    random.seed(get_username_hash(session.get("username")))
    prophecy = random.sample(ASCEND_WORDS, 10)
    resp = make_response(render_template('ascend.html', prophecy=prophecy))
    resp.set_cookie('ascend', ",".join(prophecy))
    return resp

@app.route('/lucky')
@login_required
def lucky():
    random.seed(get_username_hash(session.get("username")))
    numbers = [random.randint(1, 100) for _ in range(10)]
    resp = make_response(render_template('lucky.html', numbers=numbers))
    resp.set_cookie('lucky', ",".join(map(str, numbers)))
    return resp

@app.route('/spirit')
@login_required
def spirit():
    animals = list(SPIRITS.keys())
    animal = animals[get_username_hash(session.get("username")) % len(animals)]
    resp = make_response(render_template('spirit.html', animal=animal, image_url=SPIRITS[animal]))
    resp.set_cookie('spirit', animal)
    return resp

@app.route('/colors')
@login_required
def colors():
    random.seed(get_username_hash(session.get("username")))
    random_colors = random.sample(COLORS, 5)
    resp = make_response(render_template('colors.html', colors=random_colors))
    resp.set_cookie('colors', ",".join(random_colors))
    return resp

@app.route('/riddle')
@login_required
def riddle():
    chosen_riddle = RIDDLES[get_username_hash(session.get("username")) % len(RIDDLES)]
    resp = make_response(render_template('riddle.html', riddle=chosen_riddle))
    resp.set_cookie('riddle', chosen_riddle)
    return resp

@app.route('/social', methods=["GET", "POST", "DELETE"])
@login_required
def social():
    current_user = User.query.get(session["user_id"])
    if request.method == "POST":
        follower_username = request.form.get("follower_username")
        if follower_username:
            target = User.query.filter_by(username=follower_username).first()
            if not target:
                flash("User not found.")
                return redirect(url_for("social"))
            if target in current_user.following:
                flash("You are already following this user.")
                return redirect(url_for("social"))
            current_user.following.append(target)
            db.session.commit()
            flash("You are now following " + follower_username)
            return redirect(url_for("social"))
    if request.method == "DELETE":
        username_to_unfollow = request.args.get('username')
        target = User.query.filter_by(username=username_to_unfollow).first()
        if target and target in current_user.following:
            current_user.following.remove(target)
            db.session.commit()
            return "User unfollowed successfully"
        return "User not found", 404
    followers_list = current_user.followers.all()
    following_list = current_user.following.all()
    return render_template('following.html', followers=followers_list, following=following_list)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session["user_id"])
    return render_template('profile.html', user=user)

@app.route('/api/prophecies')
def get_prophecies():
    keys = ["ascend", "lucky", "spirit", "colors", "riddle"]
    prophecies = {key: request.cookies.get(key) for key in keys}
    return json.dumps(prophecies)

@app.route('/api/following')
@login_required
def get_following():
    username = session.get("username")
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return json.dumps({"error": "Invalid request"}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return json.dumps({"error": "User not found"})
    followers_list = [{"username": u.username} for u in user.followers.all()]
    following_list = [{"username": u.username} for u in user.following.all()]
    return json.dumps({
        "followers": followers_list,
        "following": following_list
    })