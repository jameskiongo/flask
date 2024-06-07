import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
SECRET_KEY = os.getenv("SECRET_KEY")
app.config["SECRET_KEY"] = SECRET_KEY

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
