from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests
from config import GOOGLE_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY  # セッション管理

DATABASE = "database/inst_prototype.db"

# データベース接続
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ホームページ
@app.route("/")
def home():
    if "user_id" in session:
        return render_template("search.html")
    return redirect(url_for("login"))

# ユーザー登録
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO USER (username, email, password_hash) VALUES (?, ?, ?)", 
                         (username, email, password))
            conn.commit()
            conn.close()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
    return render_template("register.html")

# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM USER WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials.", "error")
    return render_template("login.html")

# 検索ページ
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    region = request.form["region"]
    instrument = request.form["instrument"]

    # Google API検索
    url = f"https://www.googleapis.com/customsearch/v1?q={query}+{region}+{instrument}&cx={GOOGLE_CUSTOM_SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    results = response.json().get("items", [])

    return render_template("results.html", results=results)

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
