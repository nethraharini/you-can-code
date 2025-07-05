from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["MONGO_URI"] = config.MONGO_URI

mongo = PyMongo(app)

# Fixed admin pattern
ADMIN_PATTERN = "09041411"

# ========== ROUTES ==========

@app.route("/")
def home():
    return render_template("home.html")

# ---------- USER SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirmPassword")

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists!", "danger")
            return redirect(url_for("signup"))

        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": password,
            "role": "user"
        })

        flash("Account created successfully! Now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

# ---------- USER LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = mongo.db.users.find_one({"username": username})

        if user and user["password"] == password:
            session["user"] = username
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

# ---------- USER LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You've been logged out.", "info")
    return redirect(url_for("login"))

# ---------- ADMIN PATTERN ENTRY ----------
@app.route("/admin", methods=["GET", "POST"])
def admin_entry():
    if request.method == "POST":
        pattern = request.form.get("pattern")
        if pattern == ADMIN_PATTERN:
            return redirect(url_for("admin_login"))
        else:
            flash("Invalid admin pattern!", "danger")
    return render_template("admin.html")

# ---------- ADMIN LOGIN ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = mongo.db.users.find_one({"email": email, "role": "admin"})

        if admin and admin["password"] == password:
            session["admin"] = email
            flash("Welcome back, Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials or not an admin!", "danger")

    return render_template("admin_login.html")

# ---------- ADMIN DASHBOARD ----------
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" in session:
        return render_template("admin_dashboard.html")
    flash("Please login as admin", "warning")
    return redirect(url_for("admin_login"))

# ========== PROTECTED COURSE ROUTES (Placeholders) ==========
@app.route("/dsa")
def dsa():
    if "user" in session:
        return render_template("dsa.html")
    flash("Please log in to view this course.", "warning")
    return redirect(url_for("login", next=request.path))

@app.route("/oops")
def oops():
    if "user" in session:
        return render_template("oops.html")
    flash("Please log in to view this course.", "warning")
    return redirect(url_for("login", next=request.path))

@app.route("/python")
def python():
    if "user" in session:
        return render_template("python.html")
    flash("Please log in to view this course.", "warning")
    return redirect(url_for("login", next=request.path))

@app.route("/java")
def java():
    return render_template("java.html")

@app.route("/mysql")
def mysql():
    return render_template("mysql.html")

@app.route("/pandas")
def pandas():
    return render_template("pandas.html")


# (Add others like java, mysql, pandas similarly...)

# ========== MAIN ==========
if __name__ == "__main__":
    app.run(debug=True)
