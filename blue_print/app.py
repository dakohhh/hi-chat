from flask import Flask, request, redirect, render_template, url_for
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import sqlite3
from create_tables import create_database
from create_tables import generate_key
from create_tables import generate_table_id
from create_tables import create_chat_database


app = Flask(__name__)
app.secret_key = "RapemANbruh"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")



conn = sqlite3.connect('users.s3db')
wis = conn.cursor()

create_database()



@app.route("/", methods=["POST", "GET"])
def home():
    conn = sqlite3.connect('users.s3db')
    wis = conn.cursor()
    if request.method == "POST":
        user_name = request.form.get("user_name")
        id = generate_table_id()
        user_key = generate_key()
        val = (id, user_name, user_key, )
        wis.execute("INSERT INTO user VALUES(?,?,?)", val)
        conn.commit()
        create_chat_database(user_name, user_key)
        
        
        wis.execute("SELECT * FROM user")
        result = wis.fetchall()
        print(result)

        return redirect(url_for('send_message_part', user=user_name, user_key=user_key, recepient=0))
    return render_template("index.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    conn = sqlite3.connect('users.s3db')
    wis = conn.cursor()

    if request.method == "POST":
        user_key = request.form.get('key')
        wis.execute("SELECT username FROM user WHERE user_key=?", (str(user_key), ))
        user_name = wis.fetchone()
        
        if user_name == None:
            return "<h1>INVALID Key</h1>"
        else:
            return redirect(url_for('send_message_part', user=user_name[0], user_key=user_key, recepient=0))
    return render_template("login.html")

@app.route("/msg/<user>/<user_key>/<recepient>")
def send_message_part(user, user_key, recepient):

    conn = sqlite3.connect('users.s3db')
    wis = conn.cursor()
    
    wis.execute("SELECT user_key FROM user WHERE user_key=?", (user_key, ))
    som = wis.fetchone()
    if som == None:
        return "<h1>Your account Does not exist or have been deleted</h1>"
    else:
        wis.execute("SELECT username, user_key FROM user")
        result = wis.fetchall()

        get_rerecepient_name = "0"
        message_chats = None

        if recepient == "0":
            pass
        else:    
            wis.execute("SELECT username FROM user WHERE user_key=?", (recepient, ))
            get_rerecepient_name = wis.fetchone()[0]

            conn2 = sqlite3.connect(f"{user_key}.s3db")
            wis2 = conn2.cursor()

            wis2.execute(f"SELECT messages, status FROM _{str(recepient)}")
            message_chats = wis2.fetchall()
            print(message_chats)

        return render_template("message.html", display_user_name=user, display_user_key=user_key, recepient=recepient, online_users=result, display_rerecepient_name=get_rerecepient_name, message_chats=message_chats)


@app.route("/<testy>")
def test(testy):
    return f"<h1> Test works {testy}"








@socketio.on('is_online')
def is_online(json):
    print(json['check'])



@socketio.on('recieves_message')
def recieves_message(json):
    conn = sqlite3.connect('users.s3db')
    wis = conn.cursor()

    sender_key = json['sender_key']
    message = json['msg']
    reciepient_key = json['r_key']

    wis.execute("SELECT username FROM user WHERE user_key=?", (sender_key, ))
    sender = wis.fetchone()[0]
    

    data = {
        'sender': sender,
        'message': message,
        'reciepient_key': str(reciepient_key)
    }



    emit('recieve_response', data, broadcast=True)

    

@socketio.on('stores_sent_messages')
def stores_messages(json):

    conn2 = sqlite3.connect(f"{str(json['sender_key'])}.s3db")
    wis2 = conn2.cursor()

    val = (str(json['msg']), 'sent', )
    wis2.execute(f"INSERT INTO _{str(json['r_key'])} VALUES(?,?)", val)

    conn2.commit()

    
@socketio.on('store_recieving_messages')
def store_recieving_messages(json):
    conn = sqlite3.connect('users.s3db')
    wis = conn.cursor()

    wis.execute("SELECT user_key FROM user WHERE username=?", (str(json['sender']), ))
    sender_key = str(wis.fetchone()[0])


    conn2 = sqlite3.connect(f"{str(json['reciepient_key'])}.s3db")
    wis2 = conn2.cursor()
    
    val = (str(json['message']), 'recieved', )
    wis2.execute(f"INSERT INTO _{sender_key} VALUES(?,?)", val)

    conn2.commit()



socketio.run(app, debug=True)