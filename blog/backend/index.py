from config import Post, User, app, bcrypt, db
from flask import Flask, flash, redirect, render_template, request, session, url_for
from forms import LoginForm, PostForm, RegisterForm
from helpers import login_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash


## require auth to create post
## Get all posts in the db
@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate():
            try:
                hash = generate_password_hash(form.password.data)
                user = User(
                    username=form.username.data, email=form.email.data, password=hash
                )
                db.session.add(user)
                db.session.commit()
                flash("Successfully Registered")
            except SQLAlchemyError as e:
                db.session.rollback()
                error = f"Error: {e}"
                return render_template("register.html", form=form, error=error)
            return redirect("/login")

        else:
            error = []
            for key, value in form.errors.items():
                for message in value:
                    error.append(message)
            return render_template("register.html", form=form, error=error)
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate():
            try:
                email = form.email.data
                password = form.password.data
                user = User.query.filter_by(email=email).first()
                if user and check_password_hash(user.password, password):
                    session["user_id"] = user.id
                    flash("Successfully Logged In.")
                    return redirect("/")
                else:
                    return render_template(
                        "login.html", form=form, error="Invalid credentials"
                    )
            except SQLAlchemyError as e:
                error = f"Error: {e}"
                return render_template("login.html", form=form, error=error)
        else:
            error = []
            for key, value in form.errors.items():
                for message in value:
                    error.append(message)
            return render_template("login.html", form=form, error=error)

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


## Get/Create users posts in the db
@app.route("/post", methods=["POST", "GET"])
@login_required
def post():
    form = PostForm(request.form)
    if request.method == "POST":
        if form.validate():
            user_id = session["user_id"]
            try:
                post = Post(
                    title=form.title.data, content=form.content.data, user_id=user_id
                )
                db.session.add(post)
                db.session.commit()
                return redirect("/")
            except SQLAlchemyError as e:
                db.session.rollback()
                error = f"Error: {e}"
                return render_template("post.html", form=form, error=error)
    return render_template("post.html", form=form)


## Specific post based on id
@app.route("/post/<int:id>/")
def single_post(id):
    blog_post = Post.query.get_or_404(id)
    return render_template("singlepost.html", post=blog_post)


## profile page
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    if request.method == "POST":
        pass
    user = User.query.filter_by(id=user_id).first()
    print(user.image_file)
    return render_template("profile.html", user=user)

    return "/profile"


@app.route("/profile-update", methods=["GET", "POST"])
@login_required
def update_profile():
    pass


with app.app_context():
    db.create_all()
