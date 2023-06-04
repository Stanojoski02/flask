from flask import Flask, render_template, g, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os


def connect_db():
    sql = sqlite3.connect("/ask_question_forum\\question.db")
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
        return g.sqlite_db


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = get_db()
        user_cur = db.execute(f"select id, name, password, expert, admin from users where name = ?", [user])
        user_result = user_cur.fetchone()
    return user_result


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route('/')
def index():
    # user = None
    # if 'user' in session:
    #     user = session['user']
    user = get_current_user()
    return render_template('home.html', user=user)


@app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()
    if request.method == "POST":
        db = get_db()
        hashed_pw = generate_password_hash(request.form['password'], method='sha256')
        db.execute("insert into users (name, password, expert, admin) values (?,?,?,?)",
                   [request.form['name'], hashed_pw, '0', '0n '])
        db.commit()
        session['user'] = request.form['name']
        return redirect(url_for('index'))
    return render_template('register.html', user=user)


@app.route('/login', methods=["POST", "GET"])
def login():
    user = get_current_user()
    if request.method == "POST":
        db = get_db()
        name = request.form['name']
        password = request.form['password']
        user_cur = db.execute(f"select id, name, password from users where name = ?", [name])
        user_result = user_cur.fetchone()
        if check_password_hash(user_result['password'], password):
            session['user'] = name
            return redirect(url_for('index'))
        return "<h1>Password is not correct</h1>"

    return render_template('login.html', user=user)


@app.route('/question')
def question():
    user = get_current_user()
    return render_template('question.html', user=user)


@app.route('/answer')
def answer():
    user = get_current_user()
    return render_template('answer.html', user=user)


@app.route('/ask')
def ask():
    user = get_current_user()
    return render_template('ask.html', user=user)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    return render_template('unanswered.html', user=user)


@app.route('/users', methods=['GET', "POST"])
def users():
    user = get_current_user()
    db = get_db()
    users_db = db.execute('select id, name, expert, admin from users')
    my_users = users_db.fetchall()
    return render_template('users.html', user=user, users=my_users)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
