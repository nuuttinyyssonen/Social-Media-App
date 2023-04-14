from wtforms import SubmitField, StringField, PasswordField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo

class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Kirjaudu Sisään')

class Signup(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Login')

class Reset(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Send', validators=[DataRequired()])

class PasswordReset(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')