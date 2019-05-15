from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField, RadioField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from wtforms.fields.html5 import DateField
from app.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    firstName = StringField('FirstName', validators=[DataRequired()])
    lastName = StringField('Lastname', validators=[DataRequired()])
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm_password', validators=[
                                     DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[
                        DataRequired(), Regexp('^[6789]\d{9}$')])
    gender = RadioField('Gender', choices=[
                        ('male', 'Male'), ('female', 'Female')])
    date = DateField('Date of Birth', format='%d-%m-%Y',
                     validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Username already taken please choose another one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Email already taken please choose another one')

    def validate_phone_number(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('phone number is already in use')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('login')


class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Old_Password', validators=[DataRequired()])
    new_password = PasswordField('New_Password', validators=[DataRequired()])
    submit = SubmitField('update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Username already taken please choose another one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Email already taken please choose another one')


class BookTicketForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    Age = IntegerField('Age', validators=[DataRequired()])
    source = StringField('From', validators=[DataRequired()])
    destination = StringField('To', validators=[DataRequired()])
    Date = DateField('Date', format='%d-%m-%Y', validators=[DataRequired()])
    gender = RadioField('Gender', choices=[
                        ('male', 'Male'), ('female', 'Female')])
    submit = SubmitField('Book')
    fare = IntegerField('Fare', validators=[DataRequired()])
    train_name = StringField('Train_name', validators=[DataRequired()])


class SelectTrainForm(FlaskForm):
    source = StringField('From', validators=[DataRequired()])
    destination = StringField('To', validators=[DataRequired()])
    submit = SubmitField('search trains')


class BookForm(FlaskForm):
    trains = RadioField('Trains Between Stations',
                        coerce=int, validators=[DataRequired()])
    submit = SubmitField('Book')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('This is not associated with the account')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm_password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('update')
