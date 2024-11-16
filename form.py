from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Optional


class RegisterForm(FlaskForm):
    name = StringField("NAME", validators=[DataRequired()])
    password = PasswordField("PASSWORD", validators=[DataRequired()])
    email = EmailField("EMAIL", validators=[DataRequired()])
    submit = SubmitField("SUBMIT",validators=[DataRequired()])


class ListForm(FlaskForm):
    context = TextAreaField("What does to do ? ", validators=[DataRequired()])
    submit = SubmitField("OK",validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField("Your Email", validators=[DataRequired()])
    password = PasswordField("Your Password", validators=[DataRequired()])
    submit = SubmitField("Log In",validators=[DataRequired()])
