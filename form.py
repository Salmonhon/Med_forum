
from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, EmailField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, ValidationError, Optional, EqualTo
from db import Author


class Signup(FlaskForm):

    sname = StringField('Last name', validators=[DataRequired()])
    email = EmailField(validators=[DataRequired(), Email()])
    pswd = PasswordField('', validators=[DataRequired(),Length(max=8)] )
    # pswd = PasswordField('', validators=[DataRequired(),EqualTo('password_confirm', message='Passwords must match'), Length(max=8)])
    repswd = PasswordField('', validators=[DataRequired(), EqualTo('pswd', message='Passwords must match')])
    submit = SubmitField('SUBMIT')

    def validate_email(self, email):
        # print(email.data)
        author = Author.query.filter_by(email=email.data).first()
        if author:
            raise ValidationError('email registered')


class Login(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    pswd = PasswordField('Password', validators=[DataRequired(), Length(max=8)])
    submit = SubmitField('LOGIN')


class NewsForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    intro = StringField(validators=[DataRequired()])
    text = TextAreaField("Text")
    submit = SubmitField("ADD")


class SubscribeForm(FlaskForm):
    author_id = HiddenField()
    submit = SubmitField("Subscribe")


class Forgot(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()])
    submit = SubmitField('SUBMIT')


class NewPswd(FlaskForm):
    pswd = PasswordField('', validators=[DataRequired(), Length(max=8)])
    repswd = PasswordField('', validators=[DataRequired(), EqualTo('pswd', message='Passwords must match')])
    submit = SubmitField('SUBMIT')