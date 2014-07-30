ClassRank
=========

(name up for reconsideration)

A webapp that uses Collaborative Filtering to help people figure out what (specifically Georgia Tech Computer Science) classes they should take because they will be able to handle them and enjoy them.  

##Setup

(inside the environment of your choice)

1. Install Python3 (`sudo apt-get install python3` or https://www.python.org/downloads/release/python-341/)
2. Install the Tornado webserver (`pip3 install tornado`)
3. Install the scrypt hashing library (`pip3 install scrypt`)
4. Change `cookie_secret` (routing.py line 28) to something actually secure
5. `python3 routing.py runserver`
6. Set the port (default 8888)
7. Navigate to "localhost:[port]/login"
8. Login with the credentials "admin" and "password"
9. Navigate to "Admin Panel"
10. Add new schools to your whimsy
11. Change the admin password on the settings panel
12. Log out
13. Navigate to localhost:[port]/register"
14. Register an actual account and log in
15. Start using the app, you now have admin accounts and normal users
16. Rejoice