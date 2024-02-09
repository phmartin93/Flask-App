# Custom imports
from create_user import *
from post_manager import *
from models import load_user
from main import app, get_db_conn, handle_image, create_missing_profile_pictures
from forms import LoginForm, RegForm, PostForm, UserForm, CommentForm, EditForm

# Official package imports
from flask import url_for, redirect, flash, render_template, request
from flask_login import login_user, logout_user, current_user, login_required

# Creates any missing profile pictures on startup
create_missing_profile_pictures()

# '''---------------------------- HOME ----------------------------'''

# Index redirects to the home page
#  Iterates through post table in database and displays all posts
@app.route('/')
@app.route('/home')
def home():
    c = get_db_conn().cursor()
    c.execute("SELECT * FROM posts")
    posts = list(c.fetchall())
    posts.reverse()
    posts = construct_posts(posts)
    
    return render_template('home.html', posts=posts)

# '''---------------------------- LOGIN ----------------------------'''

# URL for login page
#  Will load Login Form and connect to database
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    c = get_db_conn().cursor()   

    # If statement to login user if validation passes
    #  Gets data from form and logs in the user
    if form.validate_on_submit():
        # Try block to catch TypeError caused by a username that does not exist
        try:
            c.execute(f"SELECT * FROM users WHERE username = '{form.username.data}'")
            user = list(c.fetchone())

            # Getting user by user ID
            Us = load_user(user[0])

            # Making sure username and password matches
            if form.username.data == Us.username and form.password.data == Us.password:
                # Login successful
                #  Redirects to home page
                login_user(Us, remember=form.remember.data)
                return redirect(url_for('home'))
            else:
                # Login failed
                #  Alerts that login failed and redirects back to login page
                flash('Username or password is invalid. Please try again.', 'error')
                return render_template('login.html', form=form)
        except:
            flash('Username does not exist. Please try again.', 'error')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

# '''---------------------------- REGISTER ----------------------------'''

# URL for register page
#  Will load Registration Form and create new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()

    # If statement to create user if validation passes
    #  Gets data from form and passes it into the database
    if form.validate_on_submit():
        create_new_user(form.username.data, 
                        form.password.data, 
                        form.email.data, 1)
        handle_image(form.file.data, form.username.data)
        flash('Account created! Please login.', 'success')

        return redirect(url_for('login'))
    else:
        print(form.errors)
    
    return render_template('register.html', form=form, 
                           image_file=url_for('static', filename='profile_pics/1.png'))

# '''---------------------------- CREATE POST ----------------------------'''

# URL for create post page
#  Will load Post Form and connect to database
#  Login Required to access
@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    # If statement to create post if validation passes
    #  Gets data from form and passes it into the database
    if form.validate_on_submit():
        post = [form.title.data, form.content.data, current_user.username]
        create_new_post(post)
        
        c = get_db_conn().cursor()
        c.execute(f"""SELECT *
            FROM posts
            ORDER BY post_id desc""")
        post = list(c.fetchone())

        # Redirects to post page displaying the new post
        return redirect(url_for('post', post_id=post[0], 
                                post_title=form.title.data))
    
    return render_template('create_post.html', form=form)

# '''---------------------------- POST ----------------------------'''

# URL for individual posts
#  Uses the post's ID and title to create a unique URL
#  Will load Comment Form
@app.route('/post/<post_id>/<post_title>', methods=['GET', 'POST'])
def post(post_id, post_title):
    form = CommentForm()
    # Get current post from database
    c = get_db_conn().cursor()
    c.execute(f"""SELECT *
            FROM posts
            WHERE post_id = {post_id}""")
    
    post = list(c.fetchone())

    # Get comments from database
    c = get_db_conn().cursor()
    c.execute(f"""SELECT *
            FROM comments
            WHERE post_id = {post_id}""")
    
    comments = list(c.fetchall())
    comments.reverse()
    comments = construct_comments(comments)
    
    # '''GET'''
    if request.method == 'GET':
        return render_template('post.html', form=form, post_id = post_id,  
                            post_title=post_title, content=post[2],
                            comments=comments, user = post[3])
    
    # '''POST'''
    if request.method == 'POST':
        # ON VALIDATION
        if form.validate_on_submit():
            comment = [post[0], current_user.username, form.comment.data]
            create_new_comment(comment)
            return redirect(url_for('post', post_id=post_id, 
                                    post_title=post_title))

# '''---------------------------- EDIT POST ----------------------------'''

# URL for editing a post
#  Uses the post's ID to create a unique URL
#  Will load Edit Form
#  Login Required to access
@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = EditForm()
    # Retrieve post from database
    c = get_db_conn().cursor()
    c.execute(f"""SELECT *
              FROM posts
              WHERE post_id = {post_id}""")
    
    post = list(c.fetchone())
    post = Post(post[0],post[1],post[2],post[3],post[4])
    
    # Populate the form (gives exception if populated before hand)
    if request.method == 'GET':
        # form.title.label = 'Title'
        form.title.data = post.title
        # form.content.label = 'Content'
        form.content.data = post.content

    # Updates form if validation passes
    if form.validate_on_submit():
        post.title, post.content = form.title.data, form.content.data
        update_post(post, current_user)
        return redirect(url_for('post', post_id=post_id, 
                                post_title=form.title.data))

    return render_template('edit_post.html', form=form)

# '''---------------------------- DELETE POST ----------------------------'''

# URL for deleting a post
#  Uses the post's ID to create a unique URL
#  Only deletes post upon confirmation
#  Does not load an actual page and will redirect to the home page when complete
#  Login Required to access
@app.route('/delete_post/<post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    # Retrieve post from database
    c = get_db_conn().cursor()
    c.execute(f"""SELECT *
              FROM posts
              WHERE post_id = {post_id}""")
    
    post = list(c.fetchone())
    post = Post(post[0],post[1],post[2],post[3],post[4])
    
    # Only the original poster can delete the post
    if post.user == current_user.username:
        delete_post_sql(post.id, current_user)

    return redirect(url_for('home'))

#---------------------------- EDIT COMMENT ----------------------------

# URL for editing a comment
#  Uses the comment's ID to create a unique URL
#  Will load Edit Form
#  Login Required to access
@app.route('/edit_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    form = EditForm()
    # Temporary string to prevent errors
    form.title.data = 'Random stuff so no errors are thrown :)'
    # Retrieve comments from database
    c = get_db_conn().cursor()
    c.execute(f"""SELECT *
              FROM comments
              WHERE id = {comment_id}""")
    
    comment = list(c.fetchone())
    comment = Comment(comment[0],comment[1],comment[2],comment[3],comment[4])

    # Retrieve post from database
    c.execute(f"""SELECT *
              FROM posts
              WHERE post_id = {comment.post_id}""")
    
    post = list(c.fetchone())
    post = Post(post[0],post[1],post[2],post[3],post[4])
    
    # Populate the form (gives exception if populated before hand)
    if request.method == 'GET':
        # form.content.label = 'Content'
        form.content.data = comment.content

    if form.validate_on_submit():
        comment.content = form.content.data
        update_comment(comment, current_user)
        return redirect(url_for('post', post_id=post.id, post_title=post.title))

    return render_template('edit_comment.html', form=form)

#---------------------------- DELETE COMMENT ----------------------------

# URL for deleting a comment
#  Uses the comment's ID to create a unique URL
#  Only deletes comment upon confirmation
#  Does not load an actual page and will redirect to the post page when complete
#  Login Required to access
@app.route('/delete_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    # Retrieve comment from database
    c = get_db_conn().cursor()
    c.execute(f"""SELECT *
              FROM comments
              WHERE id = {comment_id}""")
    
    comment = list(c.fetchone())
    comment = Comment(comment[0],comment[1],comment[2],comment[3],comment[4])

    # Retrieve post from database
    c.execute(f"""SELECT *
              FROM posts
              WHERE post_id = {comment.post_id}""")
    
    post = list(c.fetchone())
    post = Post(post[0],post[1],post[2],post[3],post[4])
    
    # Only the original poster can delete the comment
    if comment.user == current_user.username:
        delete_comment_sql(comment.id, current_user)

    return redirect(url_for('post', post_id=post.id, post_title=post.title))

#---------------------------- USER ----------------------------

# URL for user page
#  Uses the user's ID to create a unique URL
#  Will load User Form
#  For updating user information
#  Login Required to access
@app.route('/user/<user_id>', methods=['GET', 'POST'])
@login_required
def user(user_id):
    form = UserForm()

    # Auto validates
    if form.validate_on_submit():
        user = load_user(user_id)

        # Checks form data to update the database with any changes
        if user.username == current_user.username:
            user_dict = {}
            user_dict['password'] = form.password.data
            user_dict['email'] = form.email.data
            user_dict['user_id'] = user_id
            update_user(user_dict)

            # Checks if new profile picture has been added
            if form.file.data != None:
                handle_image(form.file.data,user.username)

            flash('Account updated!', 'success')
            return redirect(url_for('user', user_id=user_id))
        else:
            print('error validating user')
        
    return render_template('user.html', form=form)

# '''---------------------------- LOGOUT ----------------------------'''

# URL to logout
#  Does not load an actual page and will redirect to the home page when complete
#  Login Required to access
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Run the app
if __name__== "__main__":
    app.run()
