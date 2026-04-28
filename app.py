import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app=Flask(__name__)



@ app.route("/")
def home():
    return render_template("index.html")



#connect with the database:
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn


# Function to connect to your database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message=None
    if request.method == 'POST':
        fname= request.form['firstname']
        lname= request.form['lastname']
        email= request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # connect to the database
        conn = get_db_connection()
        #check first if exsit
        existing_check = conn.execute(
            f"SELECT * FROM users WHERE username = '{username}' OR password = '{password}'"
        ).fetchone()

        if existing_check:
            conn.close()
            return "Username or password already taken. Please try again."
        


        conn.execute(f"INSERT INTO users (fname, lname, email, username, password, role) VALUES ('{fname}', '{lname}','{email}','{username}', '{password}','{role}')")
        
        conn.commit()
        conn.close()
        
       # return redirect(url_for('index')) 
    
    return render_template('register.html') # we needto change this leter to make it move to anther page

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        
        # f-strings here is VULNERABLE to SQL Injection (what what we want for this phase)
        user = conn.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'").fetchone()
        
        conn.close()

        if user: # match found
            return f"Welcome back, {user['fname']}! You are logged in as {user['role']}."
        else: # no match found
            return "Invalid username or password. Please try again."

    return render_template('login.html')


if __name__=="__main__": # this should be the last line
    app.run(debug=True)