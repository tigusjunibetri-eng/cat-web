import sqlite3
from werkzeug.security import generate_password_hash


DATABASE = "cat.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    cursor = conn.cursor()

    # =========================
    # TABEL USER
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nama TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)


    # =========================
    # TABEL HASIL UJIAN
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            theta REAL,
            answered INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)


    # =========================
    # AKUN ADMIN
    # =========================

    cursor.execute("""
        SELECT id FROM users
        WHERE username = ?
    """, ("admin",))

    if cursor.fetchone() is None:

        cursor.execute("""
            INSERT INTO users
            (username, password, nama, role)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "Administrator",
            "admin"
        ))


    # =========================
    # AKUN SISWA CONTOH
    # =========================

    cursor.execute("""
        SELECT id FROM users
        WHERE username = ?
    """, ("siswa01",))

    if cursor.fetchone() is None:

        cursor.execute("""
            INSERT INTO users
            (username, password, nama, role)
            VALUES (?, ?, ?, ?)
        """, (
            "siswa01",
            generate_password_hash("siswa123"),
            "Siswa Contoh",
            "siswa"
        ))


    conn.commit()

    conn.close()