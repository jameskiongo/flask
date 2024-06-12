import json
import os

from authlib.integrations.flask_client import OAuth
from config import User, app, db
from flask import Flask, flash, redirect, render_template, session, url_for

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FLASK_SECRET = os.getenv("FLASK_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")

appConf = {
    "OAUTH2_CLIENT_ID": CLIENT_ID,
    "OAUTH2_CLIENT_SECRET": CLIENT_SECRET,
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": FLASK_SECRET,
    "FLASK_PORT": 5000,
}
oauth = OAuth(app)
app.config["SECRET_KEY"] = SECRET_KEY

oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    server_metadata_url=appConf.get("OAUTH2_META_URL"),
    client_kwargs={"scope": "openid profile email"},
)


@app.route("/")
def index():
    return render_template(
        "index.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/google-login")
def google_login():
    return oauth.myApp.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback")
def callback():
    token = oauth.myApp.authorize_access_token()
    session["user"] = token
    google_id = token.get("id_token", {})
    userinfo = token.get("userinfo", {})
    email = userinfo.get("email", {})
    user_name = userinfo.get("name", {})
    image_file = userinfo.get("picture", {})
    user = User.query.filter_by(email=email).first()
    if user:
        user.name = user_name
        user.image_file = image_file
    else:
        user = User(
            username=user_name, google_id=google_id, email=email, image_file=image_file
        )
    db.session.add(user)
    db.session.commit()
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


with app.app_context():
    db.create_all()
