# /usr/bin/env python

"""
    Main Python file for the API, checks endpoints and
    returns the appropriate data to the user.
"""

from flask import Flask, request
from flask_restful import Resource, Api
import time

app = Flask(__name__)
api = Api(app)

todos = []
latest_id = 0


class TodoResource(Resource):
    def get(self, id):
        """
            Retrieves a todo based on ID.
        """

        # return first id match in todos
        for t in todos:
            if t.get('id') == int(id):
                return t

        # return error if no match
        return {'error': 'No todo with id %s' % (id)}

    def put(self, id):
        """
            Edits a todo based on ID and provided user data.
        """

        global todos
        data = request.get_json()
        todo_index = 0
        current_time = time.time()

        # find index of first id match
        for t in todos:
            if t.get('id') == int(id):
                todo_index = todos.index(t)

        # return error if no match
        if todo_index == 0:
            return {'error': 'No todo with id %s' % (id)}

        # update with user data and new times
        todos[todo_index].update(data)
        todos[todo_index].update({
            'last_updated_at': current_time
        })
        if data.get('completed', False):
            todos[todo_index].update({
                'completed_at': current_time
            })

        return todos[todo_index]

    def delete(self, id):
        """
            Deletes a todo based on ID.
        """

        global todos

        # make new todo list without the given id
        new_todos = [t for t in todos if t.get('id') != int(id)]

        # return error if nothing was removed
        if len(new_todos) == len(todos):
            return {'error': 'No todo with id %s' % (id)}

        else:
            todos = new_todos
            return {'success': 'Deleted todo with id %s' % (id)}


class TodoListResource(Resource):
    def get(self):
        """
            Returns a list of all todos.
        """
        return todos

    def post(self):
        """
            Creates a new todo based off provided user data. A unique ID
            and certain timestamps are automatically assigned.
        """

        global todos
        global latest_id
        data = request.get_json()
        todo = {
            'id': latest_id + 1,
            'name': data.get('name', None),
            'created_at': time.time(),
            'last_updated_at': None,
            'due_date': data.get('due_date', None),
            'completed': data.get('completed', False),
            'completed_at': data.get('completed_at', None)
        }
        todos.append(todo)
        latest_id += 1
        return todo


api.add_resource(TodoResource, '/todo/<string:id>')
api.add_resource(TodoListResource, '/todos')

if __name__ == '__main__':
    app.run(debug=True)
