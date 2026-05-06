#only need this file to create our Database (only run one time)

import sqlite3
import bcrypt

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

#user table
cursor.execute('''      
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT,
            lname TEXT,
            email TEXT NOT NULL,   
            username TEXT UNIQUE NOT NULL,
            password TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            bio TEXT 
        )
    ''')

#post table 
cursor.execute('''      
        CREATE TABLE IF NOT EXISTS post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,   
            FOREIGN KEY (user_id) REFERENCES users (id)  
             
        )
    ''')


    #create the Admin account 
admin_username = "master_admin"
admin_password = "123456" 
    # Hash the password properly
hashed_pw = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
    
try:
    cursor.execute('''
        INSERT INTO users (fname, lname, email, username, password, role)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ("System", "Admin", "admin@app.com", admin_username, hashed_pw, "admin"))
        
    connection.commit()
    print("Database initialized and Admin account created")
except sqlite3.IntegrityError:
    print("dmin account already exists")


connection.commit()
connection.close()