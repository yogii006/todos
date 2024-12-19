from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/?readPreference=primary&directConnection=true&ssl=false')
db = client['inotebook']
collection = db['todo']

@app.route('/', methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        if title.strip() and desc.strip():  # Check if title and desc are not empty
            todo = {
                'title': title,
                'desc': desc,
                'date_created': datetime.utcnow()
            }
            collection.insert_one(todo)  # Insert the new todo into the MongoDB collection

    allTodo = list(collection.find())  # Retrieve all todos from MongoDB
    return render_template('index.html', allTodo=allTodo)
@app.route('/update/<string:id>', methods=['GET', 'POST'])
def update(id):
    # Convert the id from string to ObjectId before finding
    todo = collection.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        # Check if title and description are not empty
        if title and desc:
            collection.update_one(
                {'_id': ObjectId(id)},
                {'$set': {'title': title, 'desc': desc}}
            )
            return render_template('update.html', todo=todo)
            # return redirect("index.html")
        else:
            # Handle the case where title or desc is empty
            error_message = "Title and description cannot be empty."
            return render_template('index.html', todo=todo, error=error_message)

    # return render_template('update.html', todo=todo)
    return redirect("index.html")


@app.route('/delete/<string:id>')
def delete(id):
    collection.delete_one({'_id': ObjectId(id)})  # Delete the todo document by id
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=False)
