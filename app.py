from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests
from config import GOOGLE_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY  # セッション管理用の秘密鍵

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
@app.route("/search", methods=["GET", "POST"])
def search():
    conn = get_db_connection()
    if request.method == "POST":
        region = request.form.get("region", "")
        instrument = request.form.get("instrument", "")

        # 絞り込み検索
        query = "SELECT * FROM FACILITY WHERE region LIKE ?"
        facilities = conn.execute(query, (f"%{region}%",)).fetchall()
    else:
        # 全データ表示
        facilities = conn.execute("SELECT * FROM FACILITY").fetchall()

    conn.close()
    return render_template("results.html", facilities=facilities)

# Google APIで施設データを取得して保存
@app.route("/fetch_facilities")
def fetch_facilities():
    query = "全国 楽器練習場"
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={GOOGLE_CUSTOM_SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("items", [])

        if not results:
            flash("No results found from Google API.", "error")
            return redirect(url_for("home"))

        conn = get_db_connection()
        for item in results:
            name = item.get("title", "名称不明")
            link = item.get("link", "リンク不明")
            thumbnail_url = (
                item.get("pagemap", {})
                .get("cse_thumbnail", [{}])[0]
                .get("src", "サムネイル不明")
            )
            existing = conn.execute(
                "SELECT id FROM FACILITY WHERE website_url = ?", (link,)
            ).fetchone()

            if not existing:
                conn.execute(
                    """
                    INSERT INTO FACILITY (name, address, region, thumbnail_url, website_url)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (name, "不明", "全国", thumbnail_url, link),
                )

        conn.commit()
        flash("Facility data successfully fetched and stored.", "success")
    except requests.exceptions.RequestException as e:
        flash(f"An error occurred while fetching data: {e}", "error")
    finally:
        if 'conn' in locals():
            conn.close()
    return redirect(url_for("home"))

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
