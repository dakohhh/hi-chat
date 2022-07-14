from flask import Flask, render_template, redirect, url_for, request, session, flash, get_flashed_messages
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import sqlite3
from create_tables import create_database
from create_tables import generate_key
from create_tables import generate_table_id


app = Flask(__name__)
app.secret_key = "RapemanBruh"

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

create_database()

@app.route("/", methods=["POST", "GET"])
def home():
    conn  = sqlite3.connect("users.s3db")
    wis = conn.cursor()
    if request.method == "POST":
        try:
            id = generate_table_id()
            full_name = request.form.get("fname")
            username = request.form.get("username")
            wis.execute("SELECT username FROM user WHERE username=?", (username, ))
            result = wis.fetchone()
            if result == None:
                password = request.form.get("password")
                user_key = generate_key()
                phone_number = int(request.form.get("phoneno"))
                wis.execute("SELECT phoneno FROM user WHERE phoneno=?", (phone_number, ))
                result1 = wis.fetchone()
                if result1 == None:
                    print(f"{full_name} {username} {phone_number}")
                    val = (id, full_name, username, password, user_key, phone_number, )
                    wis.execute("INSERT INTO user VALUES(?,?,?,?,?,?)", val)
                    conn.commit()

                    wis.execute("SELECT fullname, username, user_key FROM user")
                    result3 = wis.fetchall()
                    print(result3)

                    session["user_info"] = [full_name, username, user_key, phone_number, result3]
                    return redirect(url_for('inbox', user=session['user_info'][1], rec=1))
                else:
                    flash("Phone number already exist")
                    return redirect(url_for('home'))
            else:
                flash("Username already exist")
                return redirect(url_for('home'))
        except ValueError:
            return "Invalid input in phone number"
    return render_template("index.html")



'''@app.route("/inbox/<user>/<rec>")
def inbox(user, rec):
    if "user_info" in session:
        return render_template("inbox.html", display_user_full_name=session["user_info"][0], display_user_name=session["user_info"][1], 
        display_user_phone_num=str(session["user_info"][3]), 
        contacts=session["user_info"][4], display_user_key=session["user_info"][2])
    else:
        return redirect(url_for("login"))'''




@app.route("/login/", methods=["POST", "GET"])
def login():
    
    conn = sqlite3.connect("users.s3db")
    wis = conn.cursor()
    if "user_info" in session:
        #return redirect(url_for('inbox', user=session['user_info'][1]), rec=1)
        return redirect(url_for('inbox', user=session["user_info"][1], rec=1))
    else:
        if request.method == "POST":
            wis.execute("SELECT username, password FROM user WHERE username=? AND password=?", (request.form.get("username"), request.form.get("password")))
            result = wis.fetchall()
            print(result)
            if result == []:
                flash("username_or_password")
                return redirect(url_for('login'))
            else:
                wis.execute("SELECT fullname, username, user_key, phoneno FROM user WHERE username=?", (request.form.get("username"), ))
                result2 = wis.fetchall()
                wis.execute("SELECT fullname, username, user_key FROM user")
                result3 = wis.fetchall()
                print(result3)
                session["user_info"] = [result2[0][0], result2[0][1], result2[0][2], result2[0][3], result3]
                #return redirect(url_for('inbox', user=session['user_info'][1]), rec=1)
                return redirect(url_for('inbox',user=result2[0][1], rec=1))
    return render_template("login.html")



@app.route("/inbox/<user>/<rec>")
def inbox(user, rec):
    if "user_info" in session:
        conn = sqlite3.connect("users.s3db")
        wis = conn.cursor()
        rec_full_name = None
        rec_user_key = None
        if rec == "1" or rec == 1:
            pass
        else:
            wis.execute("SELECT fullname FROM user WHERE username=?", (rec, ))
            rec_full_name = wis.fetchone()[0]

            wis.execute("SELECT user_key FROM user WHERE username=?", (rec, ))
            rec_user_key = wis.fetchone()[0]
        return render_template("inbox.html", display_user_full_name=session["user_info"][0], display_user_name=session["user_info"][1], 
        display_user_phone_num=str(session["user_info"][3]), 
        contacts=session["user_info"][4], display_user_key=session["user_info"][2], display_rec=rec, 
        display_rec_full_name=rec_full_name, display_rec_key = rec_user_key)
    else:return redirect(url_for("login"))



@app.route("/test/<rec>")
def test(rec):
    if "user_info" in session:
        return f'<h1>{session["user_info"][0]} {session["user_info"][1]} yeah</h1>'
    else:return redirect(url_for("login"))










@app.route("/logout")
def logout():
    if "user_info" in session:
        session.pop("user_info", None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))




@socketio.on('is_online')
def handles_connect(json):
    print(json)

@socketio.on('handle_message')
def handle_messages(json):
    print(json)
    emit('recieve_msg', json, broadcast=True)




#socketio.run(app, debug=True)
















