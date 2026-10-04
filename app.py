from flask import Flask, render_template, request, redirect, send_from_directory, session
import os
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "notenest_secret_key"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# MySQL Settings
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Naran@11'
app.config['MYSQL_DB'] = 'notenest'

mysql = MySQL(app)

# Home Page
@app.route("/")
def home():
    return render_template("home.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO users(name, email, password) VALUES(%s, %s, %s)",
            (name, email, password)
        )

        mysql.connection.commit()
        cur.close()

        return "User Registered Successfully!"

    return render_template("register.html")


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")


# Dashboard Page
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"]
        subject = request.form["subject"]

        file = request.files["file"]

        filename = file.filename

        file.save(
            os.path.join(app.config["UPLOAD_FOLDER"], filename)
        )

        cur = mysql.connection.cursor()

        user_id = session["user_id"]

        cur.execute(
              "INSERT INTO notes(title, subject, filename, user_id) VALUES(%s, %s, %s, %s)",
        (title, subject, filename, user_id)
        )

        mysql.connection.commit()
        cur.close()

        return render_template("upload_success.html")

    return render_template("upload.html")

@app.route("/notes")
def notes():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search")

    cur = mysql.connection.cursor()

    if search:

        cur.execute("""
            SELECT notes.title,
                   notes.subject,
                   notes.filename,
                   users.name
            FROM notes
            JOIN users
            ON notes.user_id = users.id
            WHERE notes.title LIKE %s
               OR notes.subject LIKE %s
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cur.execute("""
            SELECT notes.title,
                   notes.subject,
                   notes.filename,
                   users.name
            FROM notes
            JOIN users
            ON notes.user_id = users.id
        """)

    notes = cur.fetchall()

    cur.close()

    return render_template(
        "notes.html",
        notes=notes
    )

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)