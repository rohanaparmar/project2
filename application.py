import os
from flask import Flask, render_template, session, request, jsonify
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
import hashlib
import requests
from database import db
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

channels = { "public" : [{"username":"admin", "name":"admin", "message":"Welcome in chat", "date":"24-04-2020", "time":"18:39"}]}

def user_session(username,password):
    if db.execute("SELECT * FROM user_details WHERE email = :username and password = :password", {"username": username, "password": password}).rowcount == 1:
        return True;
    else:
        return False;

@app.route("/")
def index():
    return render_template("index.html")
	
@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/signup", methods = ["POST"])
def signup():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        password = (hashlib.sha256(request.form.get("password").encode())).hexdigest()
        if name is "" or password is "" or email is "":
            raise Exception;
        if db.execute("SELECT * FROM user_details WHERE email = :username", {"username": email}).rowcount == 0:
            db.execute("INSERT INTO user_details (name, email, password) VALUES (:name, :email, :password)",{"name": name, "email":email, "password": password})
            db.commit()
            return render_template("success.html", message = "Your account is created successfully")
        else:
            return render_template("error.html", message="Email already Registered")
    except Exception as e:
        return render_template("error.html", message="Invalid URL.")
    

@app.route("/login", methods = ["GET" ,"POST"])
def login():
    try:
        username = request.form.get("username")
        password = (hashlib.sha256(request.form.get("password").encode())).hexdigest()
        if username is "" or password is "":
            raise Exception;
        else:
            session["username"] = username
            session["password"] = password
    except Exception as e:
        return render_template("error.html", message=("Invalid URL.",e))
    
    if not user_session(session["username"], session["password"]):
        return render_template("error.html", message="Invalid Username And Password")
    else:
        return render_template("channels.html", messages = channels["public"], username = username, channel_list = channels.keys(),channel = "public")
    

@app.route("/logout", methods = ["GET","POST"])
def logout():
    session["username"] = ""
    session["password"] = ""
    return render_template("index.html",message = "Successfully Logout")

@app.route("/<string:channel>",methods = ["GET","POST"])
def channel(channel):
    if not user_session(session["username"], session["password"]):
            return render_template("error.html", message="Invalid URL!")
    try:
        if channel in channels:
            messages = channels[channel]
            return render_template("channels.html", messages = messages, username = session["username"], channel_list = channels.keys(), channel = channel)
        return render_template("error.html", message=("Channel is not in database!"))
    except Exception as e:
        return render_template("error.html", message=("Invalid URL!",e))

@socketio.on("submit message")
def message(data):
    message = data["message"]
    username = data["username"]
    name = db.execute("SELECT name FROM user_details WHERE email = :username", {"username": username}).fetchone()[0]
    channel = data["channel"]
    d = datetime.datetime.now()
    d1 = {"username": username, "name": name, "message": message, "date": d.strftime("%d-%m-%Y"), "time": d.strftime("%H:%M")}
    channels[channel].append(d1)
    emit("recorded message", d1, broadcast=True)

@socketio.on("create channel")
def create(data):
    print(data["channel"])
    username1 = data["username"]
    channel1 = data["channel"]
    message1 = data["message"]
    name1 = db.execute("SELECT name FROM user_details WHERE email = :username", {"username": username1}).fetchone()[0]
    d = datetime.datetime.now()
    channels[channel1] = [{"username": str(username1), "name": str(name1), "message": (str(message1)+str(name1)), "date": d.strftime("%d-%m-%Y"), "time": d.strftime("%H:%M")}]
    d1 = {"channel" : data["channel"]}
    d1.update(channels[channel1][0])
    print(channels)
    emit("created channel", d1, broadcast=True)

@socketio.on("open channel")
def open(data):
    try:
        username = data["username"]
        channel = data["channel"]
        print("\n", username, channel, "\n")
        if channel in channels:
            messages = channels[channel]
            d1 = {"messages" : messages, "username" : username, "channel" : channel}
            emit("opened channel", d1, broadcast=True) 
        else:
            d1 = { "messages" : channels["public"], "username" : username, "channel" : "public"}
            emit("opened channel", d1, broadcast=True)
    except Exception as e:
        return render_template("channels.html", messages = channels["public"], username = username, channel_list = channels.keys(),channel = "public")
