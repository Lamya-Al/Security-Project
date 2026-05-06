import sqlite3
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import bcrypt
from datetime import timedelta

app=Flask(__name__)
app.secret_key = os.urandom(24)


# Configure session cookie security settings for the Flask application
app.config.update(
    # Prevent JavaScript from accessing the session cookie
    SESSION_COOKIE_HTTPONLY=True,

    # Ensure cookies are only sent over HTTPS connections
    SESSION_COOKIE_SECURE=True,

    # Control how cookies are sent with cross-site requests
    # 'Lax' allows cookies to be sent with top-level navigation 
    SESSION_COOKIE_SAMESITE='Lax'
)

# Set the lifetime of a permanent session
app.permanent_session_lifetime = timedelta(minutes=30)
@ app.route("/")
def home():
    return render_template("index.html")


#connect with the database:
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
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        role = "user"

        # connect to the database
        conn = get_db_connection()


       #check if username OR passwrod already exists (Secure):
        query = "SELECT * FROM users WHERE username = ?"
        existing_check = conn.execute(query, (username,)).fetchone()

        if existing_check:
            conn.close()
       # conn.execute(f"INSERT INTO users (fname, lname, email, username, password, role) VALUES ('{fname}', '{lname}','{email}','{username}', '{hashed_password}
            return render_template('register.html', error="Username is already taken.")
        
        #add user to the datadase ( not Secure):
        #conn.execute(f"INSERT INTO users (fname, lname, email, username, password, role) VALUES ('{fname}', '{lname}','{email}','{username}', '{password}','{role}')")
        try:
            #add user to the datadase (Secure):
            insert_query = """
                INSERT INTO users (fname, lname, email, username, password, role) 
                VALUES (?, ?, ?, ?, ?, ?)
                """
            conn.execute(insert_query, (fname, lname, email, username, hashed_password, role))

            conn.commit()
            conn.close()
            return redirect(url_for('login')) #after rigster user need to log in

        except sqlite3.IntegrityError:
            # if the username or email is NOT UNIQUE
            conn.close()
            return render_template('register.html', error="Error: Username or Password already exists. Please choose another.") 
    
    return render_template('register.html')   

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        
        # here is VULNERABLE to SQL injection (which what we want for this phase)
        #user = conn.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'").fetchone()
        # now it is secure:
        query = "SELECT * FROM users WHERE username = ?"
        user = conn.execute(query, (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
                session['user_id'] = user['id']
                session['role'] = user['role']
                return redirect(url_for('dashboard')) #remove uid= in the URL

        else:
            return render_template('login.html', error="Invalid username or password.Please try again.")

    return render_template('login.html')

@app.route('/dashboard')

def dashboard():
    #uid = request.args.get('uid')  # not Secure
    #Secure:
    uid = session.get('user_id')
    if not uid or uid == "None":
        return redirect(url_for('login'))
    
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?",(uid,)).fetchone()
    posts = conn.execute('''
        SELECT post.content, post.timestamp, users.username 
        FROM post 
        JOIN users ON post.user_id = users.id 
        ORDER BY post.timestamp DESC
    ''').fetchall()

    conn.close()
    
    return render_template('dashboard.html', user=user, posts=posts)




@app.route("/post",methods=['GET', 'POST'])

def post():
    #uid = request.args.get('uid') or request.form.get('uid')
    # ACCESS CONTROL fixed (useing session ID):
    uid = session.get('user_id')
    print(f"DEBUG: The current UID is {uid}")
    if uid is None or uid == "":
        print("DEBUG: No UID found, redirecting to login...")
        return redirect(url_for('login'))
    

    conn = get_db_connection()
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            #  add it to the database first
            conn.execute('INSERT INTO post (user_id, content) VALUES (?, ?)', (uid, content))
            conn.commit()
            return redirect(url_for('post'))
            #return redirect(url_for('dashboard', uid=user['id']))
     # show all posts       
    posts = conn.execute('''
        SELECT post.content, post.timestamp, users.username 
        FROM post 
        JOIN users ON post.user_id = users.id 
        ORDER BY post.timestamp DESC
    ''').fetchall()
    
    user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    conn.close()

    
    return render_template('post.html', posts=posts, user=user)


# VULNERABLE - no role check
# SECURE - role check added
@app.route('/admin')

def admin():
   # uid = request.args.get('uid')
   #fixed:
    uid = session.get('user_id')
    role = session.get('role')
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    if user['role'] != 'admin':
     return render_template('access_denied.html', user=user)
    
    return render_template('admin.html', user=user, users=users)

@app.route('/logout')
def logout():
    session.clear() # Deletes the user_id and role from the session
    return redirect(url_for('login'))

if __name__ == "__main__":
    # ssl_context='adhoc' enables a temporary self-signed SSL certificate (HTTPS)
    # port=5001 sets the application to run on port 5001 instead of the default 5000
    app.run(ssl_context='adhoc', debug=True)