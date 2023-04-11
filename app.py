from flask import Flask, render_template , request , redirect, session , make_response , Response
import sqlite3
import io , csv
from datetime import datetime
from uuid import uuid4
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "crth5yjt7ynp98un"

@app.route("/")  
def index():
    return render_template("index.html")

@app.route("/login")  
def login():
    return render_template("student/index.html")

@app.route("/signin", methods =["GET", "POST"])  
def signin():
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from student WHERE email=? AND password=?",(request.form["email"],request.form["password"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            for row in rows:
                session['user']=row["id"]
            return redirect("/home")
        else:
            return redirect("/login?err=email or password is wrong!")
    return render_template("login.html")

@app.route("/register")  
def register():
    return render_template("student/register.html")

@app.route("/signup",methods = ['POST'])  
def signup():
    try:
        markfile = request.files['markfile']
        markfilename = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())+markfile.filename
        markfile.save("static/uploads/"+markfilename)
        incomefile = request.files['incomefile']
        incomefilename = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())+incomefile.filename
        incomefile.save("static/uploads/"+incomefilename)
        profffile = request.files['profffile']
        profffilename = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())+profffile.filename
        profffile.save("static/uploads/"+profffilename)
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("Insert into student(name,email,password,mobile,gender,mark,course,income,address,district,markfile,incomefile,profffile,status,donar) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(request.form["name"],request.form["email"],request.form["password"],request.form["mobile"],request.form["gender"],request.form["mark"],request.form["course"],request.form["income"],request.form["address"],request.form["district"],markfilename,incomefilename,profffilename,"no","no"))  
        con.commit()
        return redirect("/login?msg=Account Created Successfully! Try Login")
    except:
        return redirect("/login?msg=Something went Wrong!")

@app.route("/home")  
def home():
    if 'user' in session:
        user = session['user']
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from student WHERE id=?",(str(user)))  
    rows = cur.fetchall()
    for row in rows:
        if row["no"]!="no":
            cur.execute("select * from sponsor WHERE id=?",(str(row["donar"])))  
            data = cur.fetchall()
        else:
            data="no"
    return render_template("student/home.html",rows=rows,data=data)

@app.route("/sponsor/login")  
def sponsor_login():
    return render_template("sponsor/index.html")

@app.route("/sponsor/signin", methods =["GET", "POST"])  
def sponsor_signin():
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from sponsor WHERE email=? AND password=?",(request.form["email"],request.form["password"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            for row in rows:
                session['sponsor']=row["id"]
            return redirect("/sponsor/home")
        else:
            return redirect("/sponsor/login?err=email or password is wrong!")
    return render_template("sponsor/login.html")

@app.route("/sponsor/register")  
def sponsor_register():
    return render_template("sponsor/register.html")

@app.route("/sponsor/signup",methods = ['POST'])  
def sponser_signup():
    try:
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("Insert into sponsor(name,email,password,mobile,gender,address,type) values(?,?,?,?,?,?,?)",(request.form["name"],request.form["email"],request.form["password"],request.form["mobile"],request.form["gender"],request.form["address"],request.form["type"]))  
        con.commit()
        return redirect("/sponsor/login?msg=Account Created Successfully! Try Login")
    except:
        return redirect("/sponsor/login?msg=Something went Wrong!")

@app.route("/sponsor/home")  
def sponser_home():
    if 'sponsor' in session:
        sponsor = session['sponsor']
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if request.args.get("type") and request.args.get("val"):
        q = "select * from student WHERE status='yes' AND donar='no' AND "
        if request.args.get("type")=="mark":
            q=q+"mark>"+request.args.get("val")
        elif request.args.get("type")=="income":
            q=q+"income<"+request.args.get("val")
        elif request.args.get("type")=="course":
            q=q+"course='"+str(request.args.get("val"))+"'"
        elif request.args.get("type")=="district":
            q=q+"district='"+str(request.args.get("val"))+"'"
        cur.execute(q+" ORDER BY id DESC")
    else:  
        cur.execute("select * from student WHERE status=? AND donar=? ORDER BY id DESC",("yes","no"))  
    rows = cur.fetchall()
    cur.execute("select * from sponsor WHERE id=?",(str(sponsor)))  
    data = cur.fetchall()
    return render_template("/sponsor/home.html",data=data,rows=rows)

@app.route("/sponsor/list")  
def sponser_list():
    if 'sponsor' in session:
        sponsor = session['sponsor']
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from student WHERE donar=? ORDER BY id DESC",(str(sponsor)))  
    rows = cur.fetchall()
    return render_template("/sponsor/list.html",rows=rows)

@app.route("/sponsor/accept")  
def sponsor_accept():
    try:
        if 'sponsor' in session:
            sponsor = session['sponsor']
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("UPDATE student SET donar=? WHERE id=?",(sponsor,request.args.get("id")))
        con.commit()
        return redirect("/sponsor/home?msg=Accepted Successfully!")
    except:
        return redirect("/sponsor/home?err=Something went Wrong!")

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
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from student WHERE status='yes' ORDER BY id DESC")  
    student = cur.fetchall()
    cur.execute("select * from student WHERE status='deny' ORDER BY id DESC")  
    student_deny = cur.fetchall()
    cur.execute("select * from student ORDER BY id DESC")  
    student_total = cur.fetchall()
    cur.execute("select * from sponsor ORDER BY id DESC")  
    sponsor = cur.fetchall()
    cur.execute("select * from student WHERE NOT donar='no' ORDER BY id DESC")  
    donate = cur.fetchall()
    return render_template("admin/home.html",student=student,student_deny=student_deny,student_total=student_total,sponsor=sponsor,donate=donate)

@app.route("/admin/waiting")  
def waiting():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from student WHERE status='no' ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/waiting.html",rows=rows)

@app.route("/admin/approve")  
def approve():
    try:
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("UPDATE student SET status='yes' WHERE id=?",(request.args.get("id")))
        con.commit()
        return redirect("/admin/waiting?msg=Approved Successfully!")
    except:
        return redirect("/admin/waiting?err=Something went Wrong!")

@app.route("/admin/deny")  
def adeny():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("UPDATE student SET status='deny' WHERE id=?",(request.args.get("id")))
    con.commit()
    return redirect("/admin/waiting?msg=Denied Successfully!")

@app.route("/admin/student")  
def student():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from student WHERE status='yes' ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/student.html",rows=rows)

@app.route("/admin/sponsor")  
def sponsor():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from sponsor ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/sponsor.html",rows=rows)

@app.route("/table")
def table():
    con = sqlite3.connect("database.db")
    con.execute("CREATE TABLE sponsor(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL,password TEXT NOT NULL,name TEXT NOT NULL,mobile TEXT NOT NULL,gender TEXT NOT NULL,address TEXT NOT NULL,type TEXT NOT NULL)")
    con.execute("CREATE TABLE student(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT NOT NULL,password TEXT NOT NULL,name TEXT NOT NULL,course TEXT NOT NULL,income TEXT NOT NULL,mobile TEXT NOT NULL,mark TEXT NOT NULL,address TEXT NOT NULL,district TEXT NOT NULL,markfile TEXT NOT NULL,incomefile TEXT NOT NULL,gender TEXT NOT NULL,profffile TEXT NOT NULL,status TEXT NOT NULL,donar TEXT NOT NULL)")
    return "Table Created"