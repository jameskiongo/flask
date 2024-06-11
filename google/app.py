import json
import os

import requests
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for

app = Flask(__name__)
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
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read"
    },
)


@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/google-login")
def googleLogin():
    return oauth.myApp.authorize_redirect(
        redirect_uri=url_for("googleCallback", _external=True)
    )


@app.route("/signin-google")
def googleCallback():
    token = oauth.myApp.authorize_access_token()
    person_data_url = (
        "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays"
    )
    person_data = requests.get(
        person_data_url,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    ).json()
    token["person_data"] = person_data
    session["user"] = token
    return redirect("/")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))
