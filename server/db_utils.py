import sqlite3
from models import User

def nuke_db():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute('DROP TABLE users')
    connection.commit()

def init_db():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()
    cur.execute('CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, card_id INTEGER UNIQUE)')
    connection.commit()

def db_get_users():
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()

    res = cur.execute('SELECT * FROM users')

    return [User(username=user[1], card_id=user[2]) for user in res.fetchall()]

def db_add_user(user):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()

    cur.execute('INSERT INTO users(username, card_id) VALUES (?, ?)', (user.username, user.card_id))

    connection.commit()

def db_delete_user(user):
    connection = sqlite3.connect('users.db')
    cur = connection.cursor()

    cur.execute('DELETE FROM users WHERE username = ?', (user.username,))

    connection.commit()

if __name__ == '__main__':
    nuke_db()
    init_db()

    db_add_user(User(username='Biała karta', card_id=10))
    db_add_user(User(username='Krzychu', card_id=20))
    db_add_user(User(username='Janas', card_id=30))

    for user in db_get_users():
        print(user)
