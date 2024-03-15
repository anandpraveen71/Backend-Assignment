import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Function to register on the website and obtain the app_id
def register_and_get_app_id():
    # Here you should include the steps to register on the website and obtain your app_id manually
    # For this example, let's assume you have obtained your app_id manually
    return "65f213ed73be108e09604e19"

# Function to fetch users data from API
def fetch_users(api_key):
    url = "https://dummyapi.io/data/v1/user"
    headers = {'app-id': api_key}
    response = requests.get(url, headers=headers)
    return response.json()['data']

# Function to fetch posts data for a user from API
def fetch_user_posts(api_key, user_id):
    url = f"https://dummyapi.io/data/v1/user/{user_id}/post"
    headers = {'app-id': api_key}
    response = requests.get(url, headers=headers)
    return response.json()['data']

# Function to store users data in database
def store_users_in_db(users, connection):
    cursor = connection.cursor()
    for user in users:
        user_id = user.get('id')
        user_name = user.get('name', '')  # Default to empty string if 'name' key doesn't exist
        user_email = user.get('email', '')  # Default to empty string if 'email' key doesn't exist
        cursor.execute("INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                       (user_id, user_name, user_email))
    connection.commit()

# Function to store posts data in database
def store_posts_in_db(posts, connection):
    cursor = connection.cursor()
    with open("error_log.txt", "a", encoding="utf-8") as error_file:
        for post in posts:
            user_id = post.get('userId')
            if not user_id:
                error_message = f"Error: Missing key 'userId' in post data: {post}"
                print(error_message)
                error_file.write(error_message + "\n")
                cursor.execute("INSERT INTO posts (user_id, post_id, title, body) VALUES (?, ?, ?, ?)",
                               (None, None, None, error_message))  # Insert error message into database
                continue
            post_id = post.get('id')
            post_title = post.get('title', '')
            post_body = post.get('body', '')
            cursor.execute("INSERT INTO posts (user_id, post_id, title, body) VALUES (?, ?, ?, ?)",
                           (user_id, post_id, post_title, post_body))
    connection.commit()

# Function to write output for Part A
def write_output_part_a(users_data, posts_data):
    with open("output_part_a.txt", "w", encoding="utf-8") as f:
        f.write("Users and Posts Data:\n")
        for user in users_data:
            f.write(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}\n")
        
        f.write("\nPosts:\n")
        for post in posts_data:
            f.write(f"User ID: {post[0]}, Post ID: {post[1]}, Title: {post[2]}, Body: {post[3]}\n")

# Function to execute Part A
def execute_part_a():
    api_key = register_and_get_app_id()
    users = fetch_users(api_key)
    connection = sqlite3.connect("part_a.db")
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id TEXT PRIMARY KEY,
                            name TEXT,
                            email TEXT
                        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                            user_id TEXT,
                            post_id TEXT,
                            title TEXT,
                            body TEXT
                        )''')
    store_users_in_db(users, connection)
    posts_data = []
    for user in users:
        user_id = user['id']
        user_posts = fetch_user_posts(api_key, user_id)
        store_posts_in_db(user_posts, connection)
        for post in user_posts:
            posts_data.append((post.get('userId'), post.get('id'), post.get('title', ''), post.get('body', '')))
    write_output_part_a([(user['id'], user.get('name', ''), user.get('email', '')) for user in users], posts_data)
    connection.close()

# Execute Part A
execute_part_a()
