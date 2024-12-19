from flask import Flask, render_template, request, redirect, session, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'yogii006'  # Replace with a strong secret key

# MongoDB setup
client = MongoClient('mongodb+srv://yogii006:Yogesh%40nt1@arvind.liuwr.mongodb.net/')
db = client['inotebook']
users_collection = db['users']
todos_collection = db['todos']

# Routes

# Home Route
@app.route('/')
def home():
    if 'user_id' in session:
        # Get todos for the logged-in user
        user_id = session['user_id']
        all_todos = list(todos_collection.find({'user_id': ObjectId(user_id)}))
        return render_template('index.html', allTodo=all_todos)
    return redirect(url_for('login'))


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password:
            flash("Username and password are required!", "error")
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))

        # Check if the user already exists
        if users_collection.find_one({'username': username}):
            flash("Username already exists!", "error")
            return redirect(url_for('signup'))

        # Hash the password and save the user
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash("Login successful!", "success")
            return redirect(url_for('home'))

        flash("Invalid username or password!", "error")
        return redirect(url_for('login'))

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))


# Add Todo Route
@app.route('/add', methods=['POST'])
def add_todo():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    desc = request.form['desc']
    if title.strip() and desc.strip():
        todo = {
            'user_id': ObjectId(session['user_id']),  # Associate todo with the logged-in user
            'title': title,
            'desc': desc,
            'date_created': datetime.utcnow()
        }
        todos_collection.insert_one(todo)
        flash("Todo added successfully!", "success")
    return redirect(url_for('home'))


# Update Todo Route
@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update_todo(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todo = todos_collection.find_one({'_id': ObjectId(id), 'user_id': ObjectId(session['user_id'])})
    if not todo:
        flash("Todo not found!", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        if title.strip() and desc.strip():
            todos_collection.update_one(
                {'_id': ObjectId(id)},
                {'$set': {'title': title, 'desc': desc}}
            )
            flash("Todo updated successfully!", "success")
            return redirect(url_for('home'))

    return render_template('update.html', todo=todo)


# Delete Todo Route
@app.route('/delete/<string:id>')
def delete_todo(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todos_collection.delete_one({'_id': ObjectId(id), 'user_id': ObjectId(session['user_id'])})
    flash("Todo deleted successfully!", "success")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=8000)
