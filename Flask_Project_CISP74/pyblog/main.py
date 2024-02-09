import os
import sqlite3
from PIL import Image 
from flask import Flask
from flask_login import LoginManager

# Constant for the profile picture size
PROFILE_PICTURE_SIZE = (50,50)

# Flask app
app = Flask(__name__)

# Secret key needed to run the wtforms
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Login manager so users can login and logout 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Main database path
databasePath = os.path.dirname(os.path.realpath(__file__)) + '\\database.db'

# Function to connect to database
def get_db_conn():
    conn = sqlite3.connect(databasePath)
    return conn

# Function to create profile images for users
def handle_image(img,user):
    path = os.path.dirname(os.path.realpath(__file__)) + f'\\static\\profile_pictures\\temp_{img.filename}'
    # Saves data in the file field as a temporary image file that we remove later
    img.save(path)
    
    # Opens temporary file as an Image object, resizes it, then saves it as the users name
    image = Image.open(path)
    image = image.resize(PROFILE_PICTURE_SIZE)
    image = image.save(os.path.dirname(os.path.realpath(__file__)) + f'\\static\\profile_pictures\\{user}.png')
    # Removes temporary image file
    os.remove(path)

# Function to preventing app from crashing when a profile picture is missing
def create_missing_profile_pictures():
    # Connect to database and retrieve all users
    c = get_db_conn().cursor()
    c.execute("SELECT * FROM users")
    users = list(c.fetchall())
    
    # For loop to check all users' profile pictures
    #  Will assign default image if none is found
    for user in users:
        path = os.path.dirname(os.path.realpath(__file__)) + f'\\static\\profile_pictures\\{user[1]}.png'
        if os.path.isfile(path) == False:
            image = Image.open(os.path.dirname(os.path.realpath(__file__)) + f'\\static\\profile_pictures\\default.png')
            image = image.save(path)

    c.close()