import sqlite3
from flask import Flask, render_template

app=Flask(__name__)



@ app.route("/")
def home():
    return render_template("index.html")

if __name__=="__main__":
    app.run(debug=True)


#connect with the database:
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn