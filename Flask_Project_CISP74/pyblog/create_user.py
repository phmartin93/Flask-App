import sqlite3

from main import databasePath

# Database path
data = databasePath

# Function to create new user
def create_new_user(username, password, email, picture_id):
    # Connect to database
    conn = sqlite3.connect(data)

    try:
        c = conn.cursor()
        # Insert values into table
        c.execute(f"INSERT INTO users (username, password, email, picture_id) VALUES ('{username}','{password}','{email}',{picture_id})")
        # Commit changes to database
        conn.commit()
        # Show user entry has been added
        print(f'{username} added successfully to the database')
        c.close()
    except:
        print('Username is already taken.')
    finally:
        conn.close()
        print("Connection closed")

# Function to update user profile
def update_user(user_dict):
    conn = sqlite3.connect(data)

    if user_dict['email'] != 'None' and user_dict['email'] != '':
        try:
            # Create cursor
            c = conn.cursor()
            # Update record using SQL
            c.execute(f"UPDATE users SET email = '{user_dict['email']}' WHERE user_id = {user_dict['user_id']};")
            # Commit changes to database
            conn.commit()
        except:
            print('error updating email')
    if user_dict['password'] != 'None' and user_dict['password'] != '':
        try:
            # Create cursor
            c = conn.cursor()
            # Update record using SQL
            c.execute(f"UPDATE users SET password = '{user_dict['password']}' WHERE user_id = {user_dict['user_id']};")
            # Commit changes to database
            conn.commit()
        except:
            print('error updating password')