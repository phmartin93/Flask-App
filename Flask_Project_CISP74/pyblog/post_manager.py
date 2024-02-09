# Custom imports
from main import databasePath
from models import Post, Comment

# Official package imports
import sqlite3
from datetime import datetime

# This file is just to keep all the bloat out of the routes page and have somewhere to keep all the post info

################################## POSTS ##################################

# Constructs a list of post objects and returns it -> used in routes to construct home page
def construct_posts(post_list):
    #create a list to store post objects in
    new_list = []
    for post in post_list:
        #create a post object
        current_post = Post(post[0],post[1],post[2],post[3],post[4])
        new_list.append(current_post)
    return new_list

# Creates post -> used in routes create_post page
def create_new_post(post):
    # Connect to database
    conn = sqlite3.connect(databasePath)

    # Create datetime object for post date and time
    now = datetime.now()
    print((str(post[0]),str(post[1]), str(post[2]), str(now.strftime("%d/%m/%Y %H:%M:%S"))))

    try:
        # Create cursor
        c = conn.cursor()
        # Add record using SQL
        c.execute("INSERT INTO posts ('title','content','user','date') VALUES (?,?,?,?)",(str(post[0]),str(post[1]), str(post[2]), str(now.strftime("%d/%m/%Y %H:%M:%S"))))
        # Commit changes to database
        conn.commit()
    except:
        print('error adding record')

# For updating posts
def update_post(post, current_user):
    conn = sqlite3.connect(databasePath)
    try:
        # Create cursor
        c = conn.cursor()
        # Authenticates update post
        if post.user != current_user.username:
            raise ValueError
        # Update record using SQL
        c.execute("UPDATE posts SET title = ?, content = ? WHERE post_id = ? ",(post.title, post.content, post.id))
        # Commit changes to database
        conn.commit()
    except:
        print('error updating record')

# Function to delete posts
def delete_post_sql(post_id, current_user):
    conn = sqlite3.connect(databasePath)

    try:
        # Create cursor
        c = conn.cursor()
        # Get post from post_id
        c.execute(f"""SELECT * FROM posts WHERE post_id = {post_id}""")
        post = list(c.fetchone())

        # Authenticate post deletion
        #  Checks if current user is the same as post user
        if post[3] != current_user.username:
            raise ValueError
        
        # Delete record using SQL
        c.execute("DELETE FROM posts WHERE post_id =" + str(post_id))
        c.execute("DELETE FROM comments WHERE post_id =" + str(post_id))
        # Commit changes to database
        conn.commit()
        print(post_id, 'deleted')
    except:
        print('error deleting record')


################################## COMMENTS ##################################

# Function to create comments
def create_new_comment(comment):
    # Connect to database
    conn = sqlite3.connect(databasePath)

    # Create datetime object for post date and time
    now = datetime.now()
    
    try:
        # Create cursor
        c = conn.cursor()
        # Add record using SQL
        c.execute("INSERT INTO comments ('post_id','user','content', 'date') VALUES (?,?,?,?)",
                  (str(comment[0]), str(comment[1]), str(comment[2]),
                   str(now.strftime("%d/%m/%Y %H:%M:%S"))))
        # Commit changes to database
        conn.commit()
        print('working')
    except:
        print('error adding record')

# Function for constructing the list of comments under a post
def construct_comments(comment_list):
    # Create an empty list to store Comment objects
    #  Comment objects are from the models file
    new_list = []

    # For loop to iterate through the comment list
    for comment in comment_list:
        # Create a comment object
        current_comment = Comment(comment[0],comment[1],comment[2],comment[3],comment[4])
        new_list.append(current_comment)

    return new_list

# Function to update comments
def update_comment(comment, current_user):
    conn = sqlite3.connect(databasePath)

    try:
        # Create cursor
        c = conn.cursor()
        # Authenticates update comment
        if comment.user != current_user.username:
            raise ValueError
        # Update record using SQL
        c.execute("UPDATE comments SET content = ? WHERE id = ? ",(comment.content, comment.id))
        # Commit changes to database
        conn.commit()
    except:
        print('error updating record')

# Function to delete comments
def delete_comment_sql(comment_id, current_user):
    conn = sqlite3.connect(databasePath)

    try:
        # Create cursor
        c = conn.cursor()
        # Get comment
        c.execute(f"""SELECT * FROM comments WHERE id = {comment_id}""")
        comment = list(c.fetchone())

        # Authenticate comment deletion
        #  Checks if current user is the same as comment user
        if comment[2] != current_user.username:
            raise ValueError
        
        # Delete record using SQL
        c.execute("DELETE FROM comments WHERE id =" + str(comment_id))
        # Commit changes to database
        conn.commit()
        print(comment, 'deleted')
    except:
        print('error deleting record')