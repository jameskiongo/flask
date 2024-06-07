from config import User, app, bcrypt, db
from flask import redirect, render_template, request
from flask_login import login_required, login_user, logout_user
from forms import LoginForm, RegisterForm
from sqlalchemy.exc import SQLAlchemyError


@app.route("/")
@login_required
def get():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate():
            email = form.email.data
            password = form.password.data
            try:
                user = User.query.filter_by(email=email).first()

                if user and bcrypt.check_password_hash(user.password, password):
                    login_user(user)
                    return redirect("/")
                else:
                    return render_template(
                        "login.html", form=form, error="Invalid credentials"
                    )

            except SQLAlchemyError as e:
                error = f"An error occured: {e}"
                return render_template("login.html", form=form, error=error)
        else:
            error = []
            for key, value in form.errors.items():
                for message in value:
                    error.append(message)
            return render_template("login.html", form=form, error=error)

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate():
            hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            try:
                user = User(name=form.name.data, email=form.email.data, password=hashed)
                db.session.add(user)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                error = f"An error occured: {e}"
                return render_template("register.html", form=form, error=error)
            return redirect("/login")
        else:
            error = []
            for key, value in form.errors.items():
                for message in value:
                    error.append(message)
            return render_template("register.html", form=form, error=error)
    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


with app.app_context():
    db.create_all()
