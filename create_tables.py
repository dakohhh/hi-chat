import sqlite3
import random
import string




def create_database():
    conn = sqlite3.connect('users.s3db')
    wis = conn.cursor()

    wis.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, fullname text, username text, password text, user_key text UNIQUE, phoneno INTEGER UNIQUE)")

    conn.commit()




def generate_table_id():
    conn = sqlite3.connect("users.s3db")
    wis = conn.cursor()
    wis.execute("SELECT * FROM user")
    count_id = len(wis.fetchall())
    op_id = count_id + 1
    return op_id


def generate_key():
    a = ""
    for i in range(0, 7):
        a = a + str(random.choice([random.choice(string.ascii_lowercase), random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])]))
    return a





def create_chat_database(user_name, user_key):
    conn = sqlite3.connect("users.s3db")
    wis = conn.cursor()


    conn2 = sqlite3.connect(f"{user_key}.s3db")
    wis2 = conn2.cursor()



    wis.execute("SELECT user_key FROM user")
    result = wis.fetchall()

    for i in result:
        if i[0] == str(user_key):
            pass
        else:
            wis2.execute(f"CREATE TABLE IF NOT EXISTS _{str(i[0])}(messages text, status text)")

        
    conn2.commit()

    for i in result:
        conn3 = sqlite3.connect(f"{str(i[0])}.s3db")
        wis3 = conn3.cursor()

        wis3.execute(f"CREATE TABLE IF NOT EXISTS _{str(user_key)}(messages text, status text)")
        conn3.commit()
