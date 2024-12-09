import sqlite3

# データベースファイルのパス
DB_PATH = 'database/inst_prototype.db'

# データベースを初期化する関数
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # USER テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USER (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
    """)

    # INSTRUMENT テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS INSTRUMENT (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # FACILITY テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FACILITY (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        region TEXT NOT NULL,
        thumbnail_url TEXT,
        website_url TEXT
    );
    """)

    # REVIEW テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS REVIEW (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        facility_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        comment TEXT,
        FOREIGN KEY(user_id) REFERENCES USER(id),
        FOREIGN KEY(facility_id) REFERENCES FACILITY(id)
    );
    """)

    # FACILITY_INSTRUMENT テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FACILITY_INSTRUMENT (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facility_id INTEGER NOT NULL,
        instrument_id INTEGER NOT NULL,
        FOREIGN KEY(facility_id) REFERENCES FACILITY(id),
        FOREIGN KEY(instrument_id) REFERENCES INSTRUMENT(id)
    );
    """)

    # community_centers テーブルの追加
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        postal_code TEXT NOT NULL,
        address TEXT NOT NULL,
        tel TEXT,
        fax TEXT,
        thumbnail_url TEXT,
        website_url TEXT,
        map_url TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully with community_centers table!")

# 実行時にデータベースを初期化
if __name__ == "__main__":
    initialize_database()
