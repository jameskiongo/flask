import os
import re
from numbers import Number

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import apology, format_currency, format_shares, login_required, lookup, usd

# from .filters import format_currency

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["format_currency"] = format_currency
app.jinja_env.filters["format_shares"] = format_shares
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    response = db.execute(
        """
        SELECT symbol, price,SUM(shares) as shares  
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol 
        HAVING SUM(shares) > 0
    """,
        (user_id,),
    )
    sum = 0
    for r in response:
        sum += r["price"] * r["shares"]

    db_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    db_cash = round(db_cash[0]["cash"], 2)
    return render_template("index.html", response=response, cash=db_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        classification = request.form.get("type")
        if not shares or not symbol:
            return render_template("buy.html", message="Empty Fields")
        if not isinstance(shares, Number):
            return render_template("buy.html", message="Must be a number")
        if float(shares) < 0:
            return render_template("buy.html", message="Enter Valid Number")
        if classification != "buy":
            return render_template("buy.html", message="Error")
        if not isinstance(shares, Number):
            return render_template("buy.html", message="Must be a number")

        # try:
        #     input = float(shares)
        # except ValueError:
        #     return render_template("buy.html", message="Must be a number")
        symbol = lookup(symbol)
        if not symbol:
            return render_template("buy.html", message="No stock found")
        value = int(shares) * symbol["price"]
        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = cash[0]["cash"]
        if cash < value:
            return render_template("buy.html", message="Not enough Money")
        remaining = cash - value
        db.execute("UPDATE users SET cash = ? WHERE id = ?", remaining, user_id)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES (?, ?, ?, ?, ? )",
            user_id,
            symbol["symbol"],
            shares,
            symbol["price"],
            classification,
        )
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    if request.method == "GET":
        user_id = session["user_id"]
        response = db.execute("SELECT * FROM transactions WHERE user_id=?", user_id)
        return render_template("history.html", response=response)


# def format_currency(value):
#     if value < 0:
#         return abs(value)
#     return "${:,.2f}".format(value)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return render_template("quote.html", message="Empty Fields")
        symbol = lookup(symbol)
        try:
            return render_template(
                "quoted.html",
                stock_symbol=symbol["symbol"],
                stock_price=symbol["price"],
            )
        except TypeError:
            return render_template("quote.html", message="No Stock Found")

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        row_names = db.execute("SELECT * FROM users WHERE username=?", (username))
        if not username or not password or not confirm:
            return render_template("register.html", message="Empty Name")
        elif len(row_names) != 0:
            return render_template("register.html", message="Username Is Taken")
        elif len(password) < 6:
            return render_template(
                "register.html", message="Password too short (Min 6 characters)"
            )
        # elif password_check(password):
        #     return render_template(
        #         "register.html", message="Password too short (Min 6 characters)"
        #     )
        elif password != confirm:
            return render_template("register.html", message="Passwords do not match")
        else:
            hash = generate_password_hash(password)
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
            )
            session["user_id"] = new_user
            return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    response = db.execute(
        """
        SELECT symbol, SUM(shares) as shares 
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol 
        HAVING SUM(shares) > 0
    """,
        (user_id,),
    )
    if request.method == "GET":
        return render_template("sell.html", response=response)
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        classification = request.form.get("type")
        if not symbol or not shares:
            return render_template("sell.html", message="Empty Fields")
        if classification != "sell":
            return render_template("sell.html", message="Error")
        if not isinstance(shares, Number):
            return render_template("sell.html", message="Must be a number")
        if float(shares) < 0:
            return render_template("sell.html", message="Invalid Number")
        shares = float(shares)

        rows = db.execute(
            "SELECT SUM(shares) as shares FROM transactions WHERE user_id = :user_id AND symbol = :symbol",
            user_id=user_id,
            symbol=symbol,
        )
        db_shares = float(rows[0]["shares"])
        if shares > db_shares:
            return render_template(
                "sell.html", message="Not Enough shares", response=response
            )
        # remainder = db_shares - shares
        price = lookup(symbol)
        db.execute(
            "INSERT INTO transactions (user_id, symbol, shares, price, type) VALUES (?, ?, ?, ?, ? )",
            user_id,
            symbol,
            -shares,
            price["price"],
            classification,
        )

        price = lookup(symbol)
        share_price = int(price["price"])
        # shares i've sold
        # multiply by share price
        send_cash = share_price * shares
        # Add that to cash
        db_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        db_cash = db_cash[0]["cash"]
        send_to_db_cash = db_cash + send_cash

        db.execute("UPDATE users SET cash = ? WHERE id = ?", send_to_db_cash, user_id)

        return redirect("/")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "GET":
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id= ?", user_id)
        name = rows[0]["username"]

        return render_template("change.html", name=name)
    else:
        user_id = session["user_id"]
        current = request.form.get("current")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not current or not password or not confirm:
            return render_template("change.html", message="Empty Field")
        if password != confirm:
            return render_template("change.html", message="Passwords Must be the same")
        if len(password) < 6:
            return render_template("change.html", message="Passwords too short")
        rows = db.execute("SELECT * FROM users WHERE id= ?", user_id)
        if not check_password_hash(rows[0]["hash"], request.form.get("current")):
            return render_template("change.html", message="invalid password")
        hash = generate_password_hash(password)
        db.execute("UPDATE users SET hash= ? WHERE id = ?", hash, user_id)
        flash("Successfully Changed")
        session["user_id"] = rows[0]["id"]
        return redirect("/")
