 *LINKEDOUT - SECURE WEB APPLICATION*
 
A simple professional social platform inspired by LinkedIn, built with Flask and SQLite. This project demonstrates common web security vulnerabilities and their mitigations.


FEATURES

-  User Registration and Login
- Personal Dashboard with recent posts
- Explore page to share and view posts
- Role-Based Access Control (admin vs user)
- Admin Panel showing all users


THIS APPLICATION SHOWS:
  
- SQL Injection vulnerability and fix
- Weak Password Storage vulnerability and fix  
- Cross-Site Scripting (XSS) vulnerability and fix
- Role-Based Access Control (RBAC) vulnerability and fix
- Encryption using HTTPS/TLS

SECURITY TESTING GUIDE
Use the following steps to verify the security mitigations implemented in this project:

1. SQL Injection (SQLi) Prevention
Test: On the Login page, enter ' OR '1'='1' -- in the username field.

Result: Access is denied.

Mitigation: The app uses Parameterized Queries, ensuring the database treats inputs as data, not executable code.

2. XSS (Cross-Site Scripting) Prevention
Test: Create a post containing <script>alert('Hacked')</script>.

Result: The script displays as plain text on the feed; no alert box appears.

Mitigation: Jinja2 Auto-escaping sanitizes all user-generated content before rendering.


Result: The account is created as a user.

Mitigation: Role assignment is hardcoded to user on the server-side. Admins can only be created via the internal init_db.py script.

3. Broken Access Control (IDOR)
Test: Log in as a regular user and try to browse directly to https://127.0.0.1:5000/admin.

Result: The server checks the Session Role and redirects the user to an "Access Denied" page.

4. Password Security
Test: Open the database.db file with a SQLite viewer.

Result: Passwords are unreadable.

Mitigation: Bcrypt Hashing with automatic salting ensures passwords are never stored in plain text.


HOW TO RUN

1. Clone the repository:
   git clone https://github.com/Lamya-Al/Security-Project
2. Install dependencies:
   pip install -r requirements.txt
3. Initialize the database:
   python init_db.py
4. Run the application:
   python app.py
5. Open your browser at:
   http://127.0.0.1:5000
   
ADMIN CREDENTIALS
To test the Admin Panel, use the credentials created during the database initialization:
 - Username: master_admin
 - Password: 123456


TEAM MEMBERS
- Lamya
- Najd
- Jood
- Elaf
