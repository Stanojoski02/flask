from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import time

app = Flask(__name__)


def get_db_conn():
    conn = sqlite3.connect("my_users.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS my_users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()  # Close the connection before returning
    return sqlite3.connect("my_users.db")


def get_websites(username):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM websites WHERE username=?", (username,))
    websites = cursor.fetchall()
    cursor.close()
    conn.close()
    return websites


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM my_users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return redirect(url_for("success", username=username))
    else:
        return render_template("login.html", error="Invalid username or password")


@app.route("/success/<username>", methods=["GET", "POST"])
def success(username):
    if request.method == "POST":
        website = request.form["website"]
        pw = request.form["password"]
        user = request.form["username"]

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO websites (username, website, password) VALUES (?, ?, ?)", (user, website, pw))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("success", username=username))

    websites = {}
    for website in get_websites(username):
        websites[website[1]] = {
            "username": website[2],
            "password": website[3]
        }

    return render_template("websites.html", websites=websites, username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO my_users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))



if __name__ == "__main__":
    conn = get_db_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    time.sleep(1)  # Add a sleep statement before running the application
    app.run(debug=True)
