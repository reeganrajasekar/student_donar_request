from flask import Flask, render_template , request , redirect, session , make_response , Response
import sqlite3
import io , csv
from datetime import datetime
from uuid import uuid4
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "crth5yjt7ynp98un"

@app.route("/login")  
def login():
    return render_template("student/index.html")

@app.route("/signin", methods =["GET", "POST"])  
def signin():
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from user WHERE email=? AND password=?",(request.form["email"],request.form["password"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            for row in rows:
                session['user']=row["id"]
            return redirect("/home")
        else:
            return redirect("/?err=email or password is wrong!")
    return render_template("login.html")

@app.route("/register")  
def register():
    return render_template("student/register.html")

@app.route("/signup",methods = ['POST'])  
def signup():
    f = request.files['markfile']
    markfile = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())+f.filename
    f.save("static/uploads/"+markfile)  
    return render_template("student/register.html")

@app.route("/home")  
def home():
    if 'user' in session:
        user = session['user']
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from event WHERE did=? AND file='No' AND date between date('now','-2 days') AND date('now','0 days') ORDER BY id DESC",(str(user)))  
    rows = cur.fetchall()
    cur.execute("select * from event WHERE did=? AND date<date('now','-1 days') AND file='No' ORDER BY id DESC",(str(user)))  
    old = cur.fetchall()
    return render_template("home.html",rows=rows,old=old)

@app.route("/admin")  
def admin():
    return render_template("admin/index.html")

@app.route("/admin/login", methods =["GET", "POST"])  
def admin_login():
    if request.method == "POST":
        if request.form["email"]=="admin@gmail.com" and request.form["password"]=="admin":
            return redirect("/admin/home")
        else:
            return redirect("/admin?err=email or password is wrong!")
    return redirect("/admin?err=email or password is wrong!")

@app.route("/admin/home")  
def admin_home():  
    return render_template("admin/home.html")

@app.route("/admin/waiting")  
def waiting():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from student WHERE status='No' ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/waiting.html",rows=rows)



@app.route("/table")
def table():
    con = sqlite3.connect("database.db")
    con.execute("CREATE TABLE student(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL,password TEXT NOT NULL,name TEXT NOT NULL,course TEXT NOT NULL,income TEXT NOT NULL,mobile TEXT NOT NULL,mark TEXT NOT NULL,address TEXT NOT NULL,district TEXT NOT NULL,markfile TEXT NOT NULL,incomefile TEXT NOT NULL,profffile TEXT NOT NULL,status TEXT NOT NULL,donar TEXT NOT NULL)")
    return "Table Created"