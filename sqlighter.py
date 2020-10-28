import sqlite3
from random import randint
import requests
import json
import time
db = sqlite3.connect('db.db',check_same_thread=False)
sql = db.cursor()

# sql.execute("""CREATE TABLE IF EXISTS subscriptions (
#     id      INTEGER       PRIMARY KEY AUTOINCREMENT,
#     user_id VARCHAR (255) NOT NULL,
#     status  BOOLEAN       NOT NULL
#                           DEFAULT (True)
# """)
def add_subscribers(user_id,status = True):
    sql.execute("SELECT * FROM subscriptions")
    sql.execute("INSERT INTO subscriptions (user_id, status) VALUES(?,?)",(user_id,status))
    db.commit()

def subscriber_exists(user_id):
     result = sql.execute(f"SELECT * FROM subscriptions WHERE user_id = '{user_id}'").fetchall()
     db.commit()
     return bool(len(result))

def update_subscribtions(user_id, status):
    sql.execute(f"UPDATE subscriptions SET status = '{status}' WHERE user_id = '{user_id}'")
    db.commit()

def payment(user_id,sum,random_code,phone,timer):
    sql.execute("SELECT * FROM subscriptions")
    sql.execute("INSERT INTO subscriptions (user_id,sum,random_code,phone,time) VALUES(?,?,?,?,?)",(user_id,sum,random_code,phone,timer))
    db.commit()

def Time(user_id,timer):
    while timer >= 0:
        sql.execute(f"UPDATE subscriptions SET time = {timer} WHERE user_id = '{user_id}'")
        db.commit()
        timer -= 1
        time.sleep(1)
        if timer == 0:
            delete_subscribtions(user_id)
def span_subscribtions(user_id):
     result =  sql.execute(f"SELECT * FROM subscriptions  WHERE user_id = '{user_id}'").fetchall()
     db.commit()
     phone_db = result[0][3]
     sum_db = result[0][4]
     random_code_db = result[0][5]
     return print(phone_db, sum_db, random_code_db)

# def checking_subscriptions(user_id):
#     result = sql.execute(f"SELECT * FROM subscriptions WHERE user_id = '{user_id}'").fetchall()
#     db.commit()
#     status = result[0][2]
#     if status == 1:
#         return 1
#     else:
#         return 0
def delete_subscribtions(user_id):
    sql.execute(f"DELETE FROM subscriptions WHERE user_id = '{user_id}'")
    db.commit()

# user_id = '1157132020'
# span_subscribtions(user_id)
