 LINKEDOUT - SECURE WEB APPLICATION
 
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
  -Password: 123456


TEAM MEMBERS
- Lamya
- Najd
- Jood
- Elaf
