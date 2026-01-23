from db_utils import db_get_users, db_add_user, db_delete_user
from models import User
from sqlite3 import IntegrityError

def list_users(username=None, card_id=None):
    for user in db_get_users():
        if (user.username == username or username is None) and (user.card_id == card_id or card_id is None):
            print(user)

def add_user(username=None, card_id=None):
    if username is None:
        username = input("Enter username: ")
    if card_id is None:
        card_id = int(input("Enter card ID: "))
    try:
        db_add_user(User(username, card_id))
    except IntegrityError:
        print(f'Cannot add user with duplicated username of card ID!')

def delete_user(username=None):
    if username is None:
        username = input("Enter username: ")
    try:
        db_delete_user(User(username, 0))
    except IntegrityError:
        print(f'Cannot add user with duplicated username of card ID!')
