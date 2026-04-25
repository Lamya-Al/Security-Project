import sqlite3
from flask import Flask, render_template, request, redirect, url_for

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
    if request.method == 'POST':
        fname= request.form['firstname']
        lname= request.form['lastname']
        email= request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # connect to the database
        conn = get_db_connection()

        conn.execute(f"INSERT INTO users (fname, lname, email, username, password, role) VALUES ('{fname}', '{lname}','{email}','{username}', '{password}','{role}')")
        
        conn.commit()
        conn.close()
        
       # return redirect(url_for('index')) 
    
    return render_template('register.html')

if __name__=="__main__":
    app.run(debug=True)