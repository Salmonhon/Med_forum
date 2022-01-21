
from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, EmailField, PasswordField, SubmitField, TextAreaField, HiddenField,IntegerField,RadioField,FileField
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
    title = StringField("Title",validators=[DataRequired()])
    year = IntegerField(validators=[DataRequired()])
    gender = RadioField('Label', choices=[('m','Male'),('f','Female')])
    img = FileField(validators=[FileAllowed(['jpg', 'png'])])
    text = TextAreaField("Text",validators=[DataRequired()])
    submit = SubmitField("ADD")


class SubscribeForm(FlaskForm):
    author_id = HiddenField()
    submit = SubmitField("Subscribe")


class Forgot(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()])
    submit = SubmitField('SUBMIT')


class NewPswd(FlaskForm):
    pswd = PasswordField(validators=[DataRequired(), Length(max=8)])
    repswd = PasswordField( validators=[DataRequired(), EqualTo('pswd', message='Passwords must match')])
    submit = SubmitField('SUBMIT')

class AnswerButtonForm(FlaskForm):
    post_id = HiddenField()
    answer = SubmitField("Answer")


class AnswerForm(FlaskForm):
    answer = TextAreaField("Text",validators=[DataRequired()])
    submit = SubmitField('Send')

class SearchForm():
    search = TextAreaField()
    submit = HiddenField(SubmitField())

class UserForm(FlaskForm):
    user = HiddenField()
    submit = SubmitField()