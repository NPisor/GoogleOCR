import sqlite3

with sqlite3.connect("Users.db") as db:
    cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
userID INTEGER PRIMARY KEY,
username VARCHAR(20) NOT NULL,
password VARCHAR(20) NOT NULL);
''')

def addUser(username, password):
    exists = cursor.fetchall()
    cursor.execute('''SELECT username FROM user WHERE username =?''', (username,))
    if not exists:
        cursor.execute("""
            INSERT INTO user(username, password) 
                       VALUES (?,?);""", (username, password))
    db.commit()

def checkUser(username, password):
    cursor.execute("SELECT * FROM user where (userName==?) AND (password==?)", (username,password))
    exists = cursor.fetchall()
    if not exists:
        return False
    else:
        return True