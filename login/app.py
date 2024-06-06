import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session
from flask_wtf import Form
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from flask_session import Session

load_dotenv()
app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


connect = sqlite3.connect("database.db")

connect.execute(
    """CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)"""
)


class RegisterForm(Form):
    name = StringField(
        "name",
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Name"},
    )
    email = StringField(
        "email",
        validators=[
            DataRequired(),
            Email(message="Enter Valid Email"),
            Length(min=4, max=25),
        ],
        render_kw={"placeholder": "Email"},
    )
    password = PasswordField(
        "password",
        validators=[
            DataRequired(),
            Length(min=6),
            EqualTo("confirm", message="Passwords must match"),
        ],
        render_kw={"placeholder": "Password"},
    )
    confirm = PasswordField(
        render_kw={"placeholder": "Confirm Password"},
    )

    def validate_email(self, email):
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.data,))
            user = cursor.fetchone()
            if user:
                raise ValidationError("Email is already registered.")


class LoginForm(Form):
    email = StringField(
        "email",
        validators=[
            DataRequired(),
            Email(message="Enter Valid Email"),
        ],
        render_kw={"placeholder": "Email"},
    )
    password = PasswordField(
        "password",
        validators=[
            DataRequired(),
        ],
        render_kw={"placeholder": "Password"},
    )


@app.route("/")
def get():
    if not session.get("user_id"):
        return redirect("/login")
    else:
        user_id = session.get("user_id")
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email FROM users WHERE user_id= ?", (user_id,))
            user = cursor.fetchone()
            username, email = user

        return render_template("index.html", username=username)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate():
            # flash("Success")
            # return redirect("/")
            name = form.name.data
            email = form.email.data
            password = form.password.data
            hash = generate_password_hash(password)
            try:
                with sqlite3.connect("database.db") as users:
                    cursor = users.cursor()
                    cursor.execute(
                        """INSERT INTO users
                    (name, email, password) VALUES (?, ?, ?)""",
                        (name, email, hash),
                    )
                return redirect("/login")
            except sqlite3.DatabaseError as e:
                error = f"An error occured: {e}"
                render_template("register.html", form=form, error=error)

        else:
            error = []
            for key, value in form.errors.items():
                for message in value:
                    error.append(message)
            return render_template("register.html", form=form, error=error)
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    session.clear()
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate():
            email = form.email.data
            password = form.password.data
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
                user_id, username, email, db_password = user
                if user:
                    if check_password_hash(db_password, password):
                        session["user_id"] = user_id
                        return redirect("/")
                    else:
                        return render_template(
                            "login.html", form=form, error="Incorrect Password"
                        )

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")
