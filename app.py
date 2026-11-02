from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

import pandas as pd

from werkzeug.security import check_password_hash

from cat_engine.item_bank import ItemBank
from cat_engine.cat import CAT

from database import get_db, init_db


app = Flask(__name__)

app.secret_key = "cat-web-secret-key"


# ==========================================
# DATABASE
# ==========================================

init_db()


# ==========================================
# BANK SOAL
# ==========================================

df = pd.read_csv(
    "data/item_bank.csv"
)

item_bank = ItemBank(df)


# ==========================================
# CAT
# ==========================================

cat = CAT(
    item_bank=item_bank,
    max_items=10
)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )


    db = get_db()

    user = db.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    db.close()


    if user is None:

        return render_template(
            "login.html",
            error="Username atau password salah."
        )


    if not check_password_hash(
        user["password"],
        password
    ):

        return render_template(
            "login.html",
            error="Username atau password salah."
        )


    # Simpan login
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["nama"] = user["nama"]
    session["role"] = user["role"]


    # Redirect berdasarkan role

    if user["role"] == "admin":

        return redirect(
            "/admin"
        )

    else:

        return redirect(
            "/student"
        )


# ==========================================
# STUDENT DASHBOARD
# ==========================================

@app.route("/student")
def student():

    if "user_id" not in session:

        return redirect(
            "/login"
        )


    if session["role"] != "siswa":

        return redirect(
            "/login"
        )


    user = {
        "id": session["user_id"],
        "nama": session["nama"],
        "username": session["username"]
    }


    return render_template(
        "student.html",
        user=user
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    user = {
        "id": session["user_id"],
        "nama": session["nama"],
        "username": session["username"]
    }

    return render_template(
        "admin.html",
        user=user
    )


# ==========================================
# ADMIN - HASIL CAT
# ==========================================

@app.route("/admin/results")
def admin_results():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    db = get_db()

    results = db.execute(
        """
        SELECT
            results.id,
            users.username,
            users.nama,
            results.theta,
            results.answered,
            results.created_at

        FROM results

        JOIN users
        ON results.user_id = users.id

        ORDER BY results.id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin_results.html",
        results=results
    )



    if "user_id" not in session:

        return redirect(
            "/login"
        )


    if session["role"] != "admin":

        return redirect(
            "/login"
        )


    user = {
        "id": session["user_id"],
        "nama": session["nama"],
        "username": session["username"]
    }


    return render_template(
        "admin.html",
        user=user
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/login"
    )


# ==========================================
# START CAT
# ==========================================

@app.route("/start")
def start():

    if "user_id" not in session:

        return redirect(
            "/login"
        )


    if session["role"] != "siswa":

        return redirect(
            "/login"
        )


    global cat


    cat = CAT(
        item_bank=item_bank,
        max_items=10
    )


    session.pop(
        "current_item",
        None
    )


    return redirect(
        "/test"
    )


# ==========================================
# TEST
# ==========================================

@app.route("/test")
def test():

    if "user_id" not in session:

        return redirect(
            "/login"
        )


    if session["role"] != "siswa":

        return redirect(
            "/login"
        )


    if cat.is_finished():

        return redirect(
            "/result"
        )


    if "current_item" not in session:

        item = cat.get_next_item()


        if item is None:

            return redirect(
                "/result"
            )


        session["current_item"] = int(
            item.name
        )


    else:

        item_idx = session[
            "current_item"
        ]

        item = item_bank.get_item_data(
            item_idx
        )


    nomor = len(
        cat.responses
    ) + 1


    return render_template(
        "test.html",
        item=item,
        nomor=nomor,
        total=cat.max_items,
        theta=cat.get_theta()
    )


# ==========================================
# ANSWER
# ==========================================

@app.route(
    "/answer",
    methods=["POST"]
)
def answer():

    if "user_id" not in session:

        return redirect(
            "/login"
        )


    if "current_item" not in session:

        return redirect(
            "/test"
        )


    item_idx = session[
        "current_item"
    ]


    jawaban = request.form.get(
        "answer"
    )


    if not jawaban:

        return redirect(
            "/test"
        )


    jawaban = jawaban.upper()


    item = item_bank.get_item_data(
        item_idx
    )


    jawaban_benar = str(
        item["answer"]
    ).strip().upper()


    correct = (
        jawaban == jawaban_benar
    )


    cat.submit_answer(
        item_idx,
        correct
    )


    session.pop(
        "current_item",
        None
    )


    if cat.is_finished():

        return redirect(
            "/result"
        )


    return redirect(
        "/test"
    )


# ==========================================
# RESULT
# ==========================================

@app.route("/result")
def result():

    if "user_id" not in session:

        return redirect("/login")


    if session["role"] != "siswa":

        return redirect("/login")


    result = cat.get_result()


    # Simpan hasil ke database
    db = get_db()

    db.execute(
        """
        INSERT INTO results
        (user_id, theta, answered)
        VALUES (?, ?, ?)
        """,
        (
            session["user_id"],
            result["theta"],
            result["answered"]
        )
    )

    db.commit()

    db.close()


    return render_template(
        "result.html",
        result=result
    )


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )