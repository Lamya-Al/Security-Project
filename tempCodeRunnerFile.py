 query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user = conn.execute(query, (username, password)).fetchone()