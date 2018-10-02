# /usr/bin/env python
from flask import Flask, request
from flask_restful import Resource, Api
import time

app = Flask(__name__)
api = Api(app)

todos = []
latest_id = 0


class TodoResource(Resource):
    def get(self, id):
        for t in todos:
            if t.get('id') == int(id):
                return t
        return {'error': 'No todo with id %s' % (id)}

    def put(self, id):
        data = request.get_json()
        global todos
        todo_index = 0
        current_time = time.time()
        for t in todos:
            if t.get('id') == int(id):
                todo_index = todos.index(t)
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
        global todos
        new_todos = [t for t in todos if t.get('id') != int(id)]
        if len(new_todos) == len(todos):
            return {'error': 'No todo with id %s' % (id)}
        else:
            todos = new_todos
            return {'success': 'Deleted todo with id %s' % (id)}


class TodoListResource(Resource):
    def get(self):
        return todos

    def post(self):
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
