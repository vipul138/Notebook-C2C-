from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from project.models import User
import re



class RegistrationForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        pattern = re.compile("\w")
        if pattern.match(username.data):
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
        else:
            raise ValidationError("enter correct number")


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
    

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(validators=[DataRequired(), Email()])
    picture = FileField('update picture',validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class UploadBookForm(FlaskForm):
    bookname = StringField(validators=[DataRequired()])
    semester = SelectField(choices = [('1', '1 Sem'), ('2', '2 Sem'), ('3', '3 Sem'), 
                                        ('4', '4 Sem'), ('5', '5 Sem'), ('6', '6 Sem')])
    price = IntegerField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Upload')

    def validate_phone(self, phone):
        pattern = re.compile("[7-9][0-9]{9}")
        if pattern.match(phone.data):
            pass
        else:
            raise ValidationError("enter correct number")

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
