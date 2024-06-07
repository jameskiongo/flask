from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from config import User


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
    # cursor.execute("SELECT * FROM users WHERE email = ?", (email.data,))

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
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
