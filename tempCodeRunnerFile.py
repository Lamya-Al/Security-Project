if request.method == 'POST':
        fname= request.form['firstname']
        lname= request.form['lastname']
        email= request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        role = "user"