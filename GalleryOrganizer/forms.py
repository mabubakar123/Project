from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from GalleryOrganizer.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8,max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Entered Username Already Exists')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Account with Entered Email Address Already Exists')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Entered Username Already Exists')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Account with Entered Email Address Already Exists')

class PostForm(FlaskForm):
    g_image = FileField('Upload New Image', validators=[FileAllowed(['jpg','jpeg','png']), FileRequired()])
    submit = SubmitField('Upload')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class SearchForm(FlaskForm):
    image_to_be_searched = StringField('Enter Image Name', validators=[DataRequired(), Length(min=2,max=20)])
    submit = SubmitField('Search')

class ShareForm(FlaskForm):
    reciever_email = StringField('Enter Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')

class SortForm(FlaskForm):
    sort_by = SelectField('Sort by:', choices=[(1,'Name'), (2,'Date(Ascending)'), (3,'Date(Descending)'), (4,'Size(Ascending)'), (5,'Size(Descending)')], default=1, coerce=int)
    submit = SubmitField('Sort')

class RenameForm(FlaskForm):
    image_new_name = StringField('Enter New Image Name', validators=[DataRequired(), Length(min=2,max=20)])
    submit = SubmitField('Rename')