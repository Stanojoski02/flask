from flask import Flask, render_template, g, request
import sqlite3
from datetime import datetime

app = Flask(__name__)


def connect_db():
    sql = sqlite3.connect("database.db")
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/", methods=["POST", "GET"])
def index():
    conn = sqlite3.connect('database.db')
    if request.method == "POST":
        date = request.form['date']
        dt = datetime.strptime(date, "%Y-%m-%d")
        db_date = datetime.strftime(dt, "%Y%m%d")
        conn.execute("insert into log_date (entry_date) values (?)", [db_date])
    db = conn.execute("select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date"
                      " join food_date on food_date.log_date_id = log_date.id join food on food.id"
                      " = food_date.food_id order by log_date.entry_date")
    db = db.fetchall()
    pretty_results = []
    for i in db:
        single_date = {}
        d = datetime.strptime(str(i[0]), "%Y%m%d")
        single_date['entry_date'] = datetime.strftime(d, '%B %d %Y')
        d_date = i[0]
        pretty_results.append([single_date, d_date])

    conn.commit()
    conn.close()
    return render_template("home.html", results=pretty_results)


@app.route("/view/<date>", methods=["GET", "POST"])
def view(date):
    db = sqlite3.connect('database.db')
    cur = db.execute("select id,entry_date from log_date where entry_date = ?", [date])
    result = cur.fetchone()
    print(result)
    if request.method == "POST":
        print(result)
        db.execute("insert into food_date (food_id, log_date_id) values (?,?)",
                   [request.form['food-select'], result[0]])
        db.commit()

    d = datetime.strptime(str(result[1]), "%Y%m%d")
    d = datetime.strftime(d, '%B %d %Y')
    food_d = db.execute("select id, name from food")
    food_d = food_d.fetchall()
    log_cur = cur.execute(
        "select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?",
        [date])
    log_results = log_cur.fetchall()
    print(log_results)
    day = [0, 0, 0, 0]
    for i in log_results:
        day[0] += i[1]
        day[1] += i[2]
        day[2] += i[3]
        day[3] += i[4]

    db.commit()
    db.close()
    return render_template("day.html", date=d, food=food_d, results=log_results, day_data=day,
                           date_result=result[1])


@app.route("/food", methods=['GET', "POST"])
def food():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Execute a SELECT query
    cursor.execute(
        "SELECT name, protein, carbohydrates, fat, calories FROM food")  # Replace "table_name" with the actual table name
    # Fetch all rows from the result set
    foods = cursor.fetchall()
    if request.method == "POST":
        food_name = request.form["food-name"]
        protein = int(request.form["protein"])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form["fat"])
        calories = protein * 4 + carbohydrates * 4 + fat * 9
        db = sqlite3.connect('database.db')
        db.execute("insert into food (name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)",
                   [food_name, protein, carbohydrates, fat, calories])
        db.commit()
        db.close()
        return render_template("add_food.html", food_list=foods)

    return render_template("add_food.html", food_list=foods)


if __name__ == "__main__":
    app.run()
