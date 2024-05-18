import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
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
        SELECT symbol, price,SUM(shares) as shares, SUM(price) as total
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol 
    """,
        (user_id,),
    )
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
        if not shares or not symbol:
            return render_template("buy.html", message="Empty Fields")
        if float(shares) < 0:
            return render_template("buy.html", message="Enter Valid Number")
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
            "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ? )",
            user_id,
            symbol["symbol"],
            shares,
            symbol["price"],
        )
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
    # return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
