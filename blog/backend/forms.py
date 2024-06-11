from config import Post, User
from flask_wtf import Form
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class PostForm(Form):
    title = StringField(
        "name",
        validators=[DataRequired(), Length(min=1)],
        render_kw={"placeholder": "Title"},
    )
    content = TextAreaField(
        "content",
        validators=[
            DataRequired(),
            Length(min=8),
        ],
        render_kw={"placeholder": "Content"},
    )


class RegisterForm(Form):
    username = StringField(
        "username",
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Username"},
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


class UpdateForm(Form):
    username = StringField(
        "username",
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Username"},
    )
    image_file = StringField(
        "image_file",
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Image Url"},
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
