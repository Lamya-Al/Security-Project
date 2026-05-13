import sqlite3
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import bcrypt
from datetime import datetime, timedelta, UTC

# SSL imports
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure session cookie security settings
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Session lifetime
app.permanent_session_lifetime = timedelta(minutes=30)



# GENERATE SELF-SIGNED SSL CERTIFICATE

if not os.path.exists("cert.pem") or not os.path.exists("key.pem"):

    # Create private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    # Save private key
    with open("key.pem", "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Certificate details
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "SA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Riyadh"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Riyadh"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Secure Flask App"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    # Create certificate
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost")
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Save certificate
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("SSL certificate generated successfully!")






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
        #role = request.form['role']
        role = 'user'

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

    # Secure session-based authentication
    uid = session.get('user_id')

    if not uid or uid == "None":
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Get current user information
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (uid,)
    ).fetchone()

    # Get ONLY this user's posts
    posts = conn.execute('''
        SELECT post.content, post.timestamp, users.username 
        FROM post 
        JOIN users ON post.user_id = users.id 
        WHERE post.user_id = ?
        ORDER BY post.timestamp DESC
    ''', (uid,)).fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        user=user,
        posts=posts
    )




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

    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
        ssl_context=('cert.pem', 'key.pem')
    )