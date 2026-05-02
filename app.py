import sqlite3
import bcrypt
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
        role = request.form['role']

        # connect to the database
        conn = get_db_connection()
        #check first if exsit
        existing_check = conn.execute(
            f"SELECT * FROM users WHERE username = '{username}' OR password = '{hashed_password}'"
        ).fetchone()

        if existing_check:
            conn.close()
            return "Username or password already taken. Please try again."
        


        conn.execute(f"INSERT INTO users (fname, lname, email, username, password, role) VALUES ('{fname}', '{lname}','{email}','{username}', '{hashed_password}','{role}')")
        
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
       # return redirect(url_for('index')) 
    
    return render_template('register.html') # we needto change this leter to make it move to anther page

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            f"SELECT * FROM users WHERE username = '{username}'"
        ).fetchone()

        conn.close()

        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            if user['role'] == 'admin':
                return render_template('dashboard.html', user=user)
            else:
                return render_template('dashboard.html', user=user)
        else:
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    uid = request.args.get('uid')
    if not uid or uid == "None":
        return redirect(url_for('login'))
    
    
    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM users WHERE id = {uid}").fetchone()
    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM users WHERE id = {uid}").fetchone()
    posts = conn.execute('''
        SELECT post.content, post.timestamp, users.username 
        FROM post 
        JOIN users ON post.user_id = users.id 
        ORDER BY post.timestamp DESC
    ''').fetchall()


    conn.close()
    
   
    
    return render_template('dashboard.html', user=user)




@app.route("/post",methods=['GET', 'POST'])
def post():
    uid = request.args.get('uid') or request.form.get('uid')
    print(f"DEBUG: The current UID is {uid}")
    if uid is None or uid == "":
        print("DEBUG: No UID found, redirecting to login...")
        return redirect(url_for('login'))
    

    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM users WHERE id = {uid}").fetchone()
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            #  add it to the database first
            conn.execute(f'INSERT INTO post (user_id, content) VALUES ({uid}, "{content}")')
            conn.commit()
            return redirect(url_for('post', uid=uid))
            #return redirect(url_for('dashboard', uid=user['id']))
     # show all posts       
    posts = conn.execute('''
        SELECT post.content, post.timestamp, users.username 
        FROM post 
        JOIN users ON post.user_id = users.id 
        ORDER BY post.timestamp DESC
    ''').fetchall()
    
    user = conn.execute(f"SELECT * FROM users WHERE id = {uid}").fetchone()
    conn.close()

    
    return render_template('post.html', posts=posts, user=user)




if __name__=="__main__": # this should be the last line
    app.run(debug=True)
