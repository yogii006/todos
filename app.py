# from flask import Flask, render_template, request, redirect
# from pymongo import MongoClient
# from bson.objectid import ObjectId
# from datetime import datetime

# app = Flask(__name__)

# client = MongoClient('mongodb+srv://yogii006:Yogesh%40nt1@arvind.liuwr.mongodb.net/')
# db = client['inotebook']
# collection = db['todo']

# @app.route('/', methods=['GET', 'POST'])
# def hello_world():
#     if request.method == 'POST':
#         title = request.form['title']
#         desc = request.form['desc']
#         if title.strip() and desc.strip():  # Check if title and desc are not empty
#             todo = {
#                 'title': title,
#                 'desc': desc,
#                 'date_created': datetime.utcnow()
#             }
#             collection.insert_one(todo)  # Insert the new todo into the MongoDB collection

#     allTodo = list(collection.find())  # Retrieve all todos from MongoDB
#     return render_template('index.html', allTodo=allTodo)
# @app.route('/update/<string:id>', methods=['GET', 'POST'])
# def update(id):
#     # Convert the id from string to ObjectId before finding
#     todo = collection.find_one({'_id': ObjectId(id)})

#     if request.method == 'POST':
#         title = request.form['title']
#         desc = request.form['desc']

#         # Check if title and description are not empty
#         if title and desc:
#             collection.update_one(
#                 {'_id': ObjectId(id)},
#                 {'$set': {'title': title, 'desc': desc}}
#             )
#             return render_template('update.html', todo=todo)
#             # return redirect("index.html")
#         else:
#             # Handle the case where title or desc is empty
#             error_message = "Title and description cannot be empty."
#             return render_template('index.html', todo=todo, error=error_message)

#     # return render_template('update.html', todo=todo)
#     return redirect("index.html")


# @app.route('/delete/<string:id>')
# def delete(id):
#     collection.delete_one({'_id': ObjectId(id)})  # Delete the todo document by id
#     return redirect("/")

# if __name__ == "__main__":
#     app.run(debug=True, port=8000)
    
from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
client = MongoClient(os.getenv("MONGO_URI"))
db = client['inotebook']
users = db['users']       # Collection for user authentication
todos = db['todos']       # Collection for todos

# Routes

# Home Route
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        if title.strip() and desc.strip():
            todo = {
                'title': title,
                'desc': desc,
                'date_created': datetime.utcnow(),
                'user_id': session['user_id']  # Associate todo with the logged-in user
            }
            todos.insert_one(todo)

    user_todos = list(todos.find({'user_id': session['user_id']}))
    return render_template('index.html', allTodo=user_todos, user_name=session['name'])


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        if users.find_one({'email': email}):
            return "Email already registered!"

        # Hash the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user
        users.insert_one({'name': name, 'email': email, 'password': hashed_pw})
        return redirect('/login')

    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find user in database
        user = users.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            session['name'] = user['name']
            return redirect('/')
        return "Invalid Credentials!"

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# Update Todo Route
@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    if 'user_id' not in session:
        return redirect('/login')

    todo = todos.find_one({'_id': ObjectId(id), 'user_id': session['user_id']})
    if not todo:
        return "Todo not found or you don't have access to it."

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        if title.strip() and desc.strip():
            todos.update_one(
                {'_id': ObjectId(id)},
                {'$set': {'title': title, 'desc': desc}}
            )
            return redirect('/')

    return render_template('update.html', todo=todo)


# Delete Todo Route
@app.route('/delete/<string:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')

    todos.delete_one({'_id': ObjectId(id), 'user_id': session['user_id']})
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=8000)

