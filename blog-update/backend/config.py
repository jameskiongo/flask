from datetime import datetime

from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
db = SQLAlchemy(app)


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(125), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="post", lazy=True)

    def __repr__(self):
        return f"<Post {self.title}>"


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.Text, unique=True, nullable=False)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)
    image_file = db.Column(
        db.Text,
        nullable=True,
        default="https://media.istockphoto.com/id/1300845620/vector/user-icon-flat-isolated-on-white-background-user-symbol-vector-illustration.jpg?s=612x612&w=0&k=20&c=yBeyba0hUkh14_jgv1OKqIH0CCSWU_4ckRkAoy2p73o=",
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
