# Sample code with deliberate flaws to verify the bot live in demo
import sqlite3

def get_user_data(user_id):
    # Bug 1: SQL Injection vulnerability
    query = "SELECT * FROM users WHERE id = '" + str(user_id) + "'"
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def parse_config(path):
    # Bug 2: Unhandled Exception / Resource leak without context manager
    f = open(path, "r")
    data = f.read()
    return data
