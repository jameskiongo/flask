import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

from flask_session import Session

load_dotenv()
app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
SECRET_KEY = os.getenv("SECRET_KEY")
app.config["SECRET_KEY"] = SECRET_KEY


class MyForm(FlaskForm):
    name = StringField(
        "name", validators=[DataRequired()], render_kw={"placeholder": "Name"}
    )
    email = StringField(
        "email", validators=[DataRequired()], render_kw={"placeholder": "Email"}
    )
    password = PasswordField(
        "password", validators=[DataRequired()], render_kw={"placeholder": "Password"}
    )
    confirm = PasswordField(
        "confirm",
        validators=[DataRequired()],
        render_kw={"placeholder": "Confirm Password"},
    )


@app.route("/")
def get():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass
    else:
        form = MyForm()
        if form.validate_on_submit():
            return redirect("/")
        return render_template("login.html", form=form)


@app.route("/register")
def register():
    return "register"


@app.route("/logout")
def logout():
    return "logout"
