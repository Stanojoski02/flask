import sqlite3

# Connect to the database
conn = sqlite3.connect('question.db')
cursor = conn.cursor()

# Create the users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        expert BOOLEAN NOT NULL,
        admin BOOLEAN NOT NULL
    )
''')

# Create the questions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_text TEXT NOT NULL,
        answer_text TEXT,
        asked_by_id INTEGER NOT NULL,
        expert_id INTEGER NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
