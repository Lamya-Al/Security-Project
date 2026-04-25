#only need this file to create our Database (only run one time)
import sqlite3

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

#post table (maybe remove it?)
cursor.execute('''      
        CREATE TABLE IF NOT EXISTS post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,   
            FOREIGN KEY (user_id) REFERENCES users (id)  
             
        )
    ''')

connection.commit()
connection.close()