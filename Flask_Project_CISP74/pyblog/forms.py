# Custom imports
from main import get_db_conn

# Official package imports
#  Must install wtforms email package along with base package
#  Use pip install wtforms[email] for the email package
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import validators, StringField, PasswordField, SubmitField, EmailField, ValidationError, TextAreaField, BooleanField
from wtforms.validators import *

# Login Form
#  Has fields to input username and password
#  Has a field to remember login if page is closed
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()], 
                           render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[InputRequired()], 
                             render_kw={'placeholder': 'Password'})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Registration Form
#  Has fields to input username and password
#  Must confirm password by typing it in again
#  Has a field to upload a profile picture that is a png, jpg, or jpeg file type
class RegForm(FlaskForm):
    username = StringField('Username', 
                           validators=[InputRequired(), Length(min=4, max=15)], 
                           render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', 
                             validators=[InputRequired(), Length(min=8, max=30)], 
                             render_kw={'placeholder': 'Password'})
    confirmPass = PasswordField('Confirm Password', 
                                validators=[InputRequired(), EqualTo('password')], 
                                render_kw={'placeholder': 'Confirm Password'})
    email = EmailField('Email', validators=[InputRequired(), Email()], 
                       render_kw={'placeholder': 'Email'})
    file = FileField('Profile Picture', validators=[FileRequired(), 
                                                    FileAllowed(['png', 'jpg', 'jpeg'], 
                                                                'Invalid File Type. Must be .png, .jpeg')])
    submit = SubmitField('Register')
    

    # Username validation
    #  It will run automatically when the form is submitted
    #  Connects to database and checks to see if username is a duplicate
    #  Raises ValidationError if duplicate is found
    def validate_username(self, username):
        c = get_db_conn().cursor()
        c.execute(f"SELECT EXISTS(SELECT * FROM users WHERE username='{username.data}')")

        if c.fetchone() == (1,):
            raise ValidationError('Username already exists. Please enter another one.')

    # Email validation
    #  It will run automatically when the form is submitted
    #  Connects to database and checks to see if email is a duplicate
    #  Raises ValidationError if duplicate is found    
    def validate_email(self, email):
        c = get_db_conn().cursor()
        c.execute(f"SELECT EXISTS(SELECT * FROM users WHERE email='{email.data}')")

        if c.fetchone() == (1,):
            raise ValidationError('Email already exists. Please enter another one.')

# Post Form
#  Has fields to submit a title and content body of a post
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], 
                        render_kw={'placeholder': 'Title'})
    content = TextAreaField('Content', validators=[DataRequired()], 
                            render_kw={'placeholder': 'Content'})
    submit = SubmitField('Post')

# Edit Form
#  Similar to the Post Form, but is used for editing purposes only
#  Has no validators since it is for editing. No changes have to be made
class EditForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content')
    submit = SubmitField('Update')

# Comment Form
#  Similar to the Post Form, but lacks the title field
class CommentForm(FlaskForm):
    comment = TextAreaField(validators=[DataRequired()], 
                            render_kw={'placeholder': 'Leave a comment...'})
    submit = SubmitField('Post')

# User Form
#  Similar to the Register Form, but lacks the username field and its validation
#  Still has the email validation
class UserForm(FlaskForm):
    password = PasswordField('Password', 
                             validators=[Length(min=8, max=30), validators.Optional()], 
                             render_kw={'placeholder': 'New Password'})
    confirmPass = PasswordField('Confirm Password', 
                                validators=[EqualTo('password'), validators.Optional()], 
                                render_kw={'placeholder': 'Confirm Password'})
    
    email = EmailField('Email', validators=[Email(), validators.Optional()], 
                       render_kw={'placeholder': 'Email'})
    file = FileField('Profile Picture', validators=[FileAllowed(['png', 'jpg', 'jpeg'], 
                                                                'Invalid File Type. Must be .png, .jpeg, or .jpg')])
    submit = SubmitField('Update Profile')

    # Email validation
    #  It will run automatically when the form is submitted
    #  Connects to database and checks to see if email is a duplicate
    #  Raises ValidationError if duplicate is found   
    def validate_email(self, email):
        c = get_db_conn().cursor()
        c.execute(f"SELECT EXISTS(SELECT * FROM users WHERE email='{email.data}')")

        if c.fetchone() == (1,):
            raise ValidationError('Email already exists. Please enter another one.')
