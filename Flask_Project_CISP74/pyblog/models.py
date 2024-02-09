# Custom imports
from main import login_manager, get_db_conn

# Official package imports
from flask_login import UserMixin

# Function to load the user logging in
#  Connects to database and fetches user information
#  Only activates upon successful login
@login_manager.user_loader
def load_user(user_id):
    c = get_db_conn().cursor()
    c.execute(f"SELECT * FROM users WHERE user_id = {user_id};")
    user = c.fetchone()

    if user is None:
        return None
    else:
        return User(int(user[0]), user[1], user[2])
    
# Function to load posts
#  Connects to database and fetches post information
def load_post(post_id):
    c = get_db_conn().cursor()
    c.execute(f"SELECT * FROM posts WHERE post_id = {post_id};")
    post = c.fetchone()

    if post is None:
        return None
    else:
        return Post()

###### USER MODEL ######
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.authenticated = False

    def is_active(self):
        return self.is_active()
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return self.authenticated
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.id

###### POST MODEL ######
class Post():
    def __init__(self, id, title, content, user, date) -> None:
        self.id = id
        self.title = title
        self.content = content
        self.user = user
        self.date = date
    
###### COMMENT MODEL ######    
class Comment():
    def __init__(self, id, post_id, user, content, date):
        self.id = id
        self.post_id = post_id
        self.content = content
        self.user = user
        self.date = date