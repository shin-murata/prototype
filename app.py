from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from config import GOOGLE_API_KEY, GOOGLE_CUSTOM_SEARCH_ENGINE_ID, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY  # セッション管理用の秘密鍵

DATABASE = "database/inst_prototype.db"

# データベース接続
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 辞書形式でクエリ結果を取得する設定
    return conn

# ホームページ
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("search"))
    return redirect(url_for("login"))

# ユーザー登録
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO USER (username, email, password_hash) VALUES (?, ?, ?)",
                           (username, email, password))  # SQLiteではプレースホルダーは "?" を使用
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM USER WHERE email = ?", (email,))  # SQLiteでは "?" を使用
        user = cursor.fetchone()
        cursor.close()
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
    cursor = conn.cursor()

    if request.method == "POST":
        region = request.form.get("region", "")
        query = """
        SELECT * FROM community_centers
        WHERE address LIKE ? OR name LIKE ?
        """
        cursor.execute(query, (f"%{region}%", f"%{region}%"))  # SQLiteでは "?" を使用
        facilities = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM community_centers")
        facilities = cursor.fetchall()

    cursor.close()
    conn.close()

    # テンプレートにデータを渡す
    return render_template("search.html", facilities=facilities)

# ログアウト
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

# デバッグ用エンドポイント
@app.route("/debug")
def debug():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # community_centersテーブルのデータを取得
        cursor.execute("SELECT * FROM community_centers")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return {"data": [dict(row) for row in rows]}, 200  # データを辞書形式に変換して返す
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
