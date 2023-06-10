from flask import Flask, render_template, g, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os


def connect_db():
    sql = sqlite3.connect('question.db')
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
        sql = sqlite3.connect('question.db')
        sql.row_factory = sqlite3.Row
        g.sqlite_db = sql
        db = g.sqlite_db
        user_cur = db.execute(f"select id, name, password, expert, admin from users where name = ?", [user])
        user_result = user_cur.fetchone()
    return user_result


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route('/')
def index():
    user = get_current_user()
    sql = sqlite3.connect('question.db')
    sql.row_factory = sqlite3.Row
    g.sqlite_db = sql
    db = g.sqlite_db
    if user:
        questions = db.execute(
            f"select questions.id, questions.question_text,"
            f" askers.name as asker_name, "
            f"experts.name as expert_name from questions join users"
            f" as askers on "
            f"askers.id = questions.asked_by_id join users as experts on experts.id = questions.expert_id "
            f"where questions.answer_text is not null")
        questions = questions.fetchall()
        user = get_current_user()
    else:
        questions = []
    db.commit()
    db.close()
    return render_template('home.html', user=user, questions=questions)


@app.route('/register', methods=["POST", "GET"])
def register():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == "POST":
        db = get_db()
        name = request.form['name']
        same_name = db.execute(f"select * from users where name = '{name}'")
        if same_name:
            return render_template('register.html', user=user, error_msg="User Already Exist!!")
        hashed_pw = generate_password_hash(request.form['password'], method='sha256')
        db.execute("insert into users (name, password, expert, admin) values (?,?,?,?)",
                   [name, hashed_pw, '0', '0'])
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
        if not user_result:
            return render_template('login.html', user=user, error_msg="This user dont exist try agen")
        if check_password_hash(user_result['password'], password):
            session['user'] = name
            return redirect(url_for('index'))
        return "<h1>Password is not correct</h1>"

    return render_template('login.html', user=user)


@app.route('/question/<my_id>')
def question(my_id):
    user = get_current_user()
    sql = sqlite3.connect('question.db')
    sql.row_factory = sqlite3.Row
    g.sqlite_db = sql
    db = g.sqlite_db
    question_ = db.execute(f"select * from questions where questions.id = {my_id}")
    question_ = question_.fetchone()
    asker = db.execute(f"select * from users where id = {question_['asked_by_id']}")
    asker = asker.fetchone()
    answerer = db.execute(f"select * from users where id = {question_['expert_id']}")
    answerer = answerer.fetchone()
    db.commit()
    db.close()
    return render_template('question.html', user=user, question_=question_, asker=asker, answerer=answerer)


@app.route('/answer/<question_id>', methods=["POST", "GET"])
def answer(question_id):
    user = get_current_user()
    if not user['expert']:
        return redirect(url_for('login'))
    sql = sqlite3.connect('question.db')
    sql.row_factory = sqlite3.Row
    g.sqlite_db = sql
    db = g.sqlite_db
    question_text = db.execute(f"select * from questions where id = {question_id}")
    question_text = question_text.fetchone()

    if request.method == "POST":
        db.execute(f"update questions set answer_text = '{request.form['text']}' where id = {question_id}")
        db.commit()
        db.close()
        return redirect(url_for('unanswered'))
    return render_template('answer.html', user=user, question_text=question_text)


# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS questions (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         question_text TEXT NOT NULL,
#         answer_text TEXT,
#         asked_by_id INTEGER NOT NULL,
#         expert_id INTEGER NOT NULL
#     )
# ''')
# db.execute("insert into users (name, password, expert, admin) values (?,?,?,?)",
@app.route('/ask', methods=["POST", "GET"])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    sql = sqlite3.connect('question.db')
    sql.row_factory = sqlite3.Row
    g.sqlite_db = sql
    db = g.sqlite_db
    if request.method == "POST":
        db.execute('insert into questions (question_text, asked_by_id, expert_id) values (?,?,?)',
                   [request.form['question'], user['id'], request.form['expert']])
        db.commit()
        return redirect(url_for('index'))

    experts = db.execute("select * from users where expert = 1")
    experts = experts.fetchall()
    return render_template('ask.html', user=user, experts=experts)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    sql = sqlite3.connect('question.db')
    sql.row_factory = sqlite3.Row
    g.sqlite_db = sql
    db = g.sqlite_db
    questions = db.execute(
        'select questions.id, questions.question_text, users.name from questions'
        ' join users on users.id = questions.asked_by_id'
        ' where questions.answer_text is null and questions.expert_id = ?',
        [user['id']])
    questions = questions.fetchall()

    return render_template('unanswered.html', user=user, questions=questions)


@app.route('/users', methods=['GET', "POST"])
def users():
    user = get_current_user()
    if not user['admin']:
        return redirect(url_for('login'))
    sql = sqlite3.connect('question.db')
    sql.row_factory = sqlite3.Row
    g.sqlite_db = sql
    db = g.sqlite_db

    if db:
        users_db = db.execute('select id, name, expert, admin from users')
        my_users = users_db.fetchall()
        for i in my_users:
            print(i['name'], type(i['admin']))
        return render_template('users.html', user=user, users=my_users)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))


@app.route('/promote/<user_id>')
def promote(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    admin = db.execute(f'select expert from users where id = {user_id}')
    admin = admin.fetchone()
    if admin['expert'] == 0:
        db.execute(f"update users set expert = 1 where id = {user_id}")
    else:
        db.execute(f"update users set expert = 0 where id = {user_id}")
    db.commit()
    db.close()
    return redirect(url_for('users'))


if __name__ == '__main__':
    app.run(debug=True)
