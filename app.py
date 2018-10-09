# /usr/bin/env python

"""
    Main Python file for the API, checks endpoints and
    returns the appropriate data to the user.
"""

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import time
import logging
from logging.handlers import RotatingFileHandler

# flask stuff
app = Flask(__name__)
api = Api(app)

# logging stuff
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(filename)s : %(message)s')
LOGFILE = "./todos.log"
handler = RotatingFileHandler(
    LOGFILE, mode='a', maxBytes=5*1024*1024,
    backupCount=2, encoding=None, delay=0)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# parser stuff
parser = reqparse.RequestParser()

# variables
todos = []
latest_id = 0


class TodoResource(Resource):
    def get(self, id):
        """
            Retrieves a todo based on ID.
        """
        logger.info('Recieved GET request for todo ID {}'.format(id))
        for t in todos:
            if t.get('id') == int(id):
                logger.info('Responded with todo:')
                logger.info(t)
                return t
        logger.error('Responded with error, no ID match')
        return {'error': 'No todo with id %s' % (id)}

    def put(self, id):
        """
            Edits a todo based on ID and provided user data.
        """
        global todos
        data = request.get_json()
        todo_index = -1
        current_time = time.time()
        logger.info('Recieved PUT request for ID {}:'.format(id))
        logger.info(data)
        for t in todos:
            if t.get('id') == int(id):
                todo_index = todos.index(t)
        if todo_index == -1:
            logger.error('Responded with error, no ID match')
            return {'error': 'No todo with id %s' % (id)}
        todos[todo_index].update(data)
        todos[todo_index].update({
            'last_updated_at': current_time
        })
        if data.get('completed', False):
            todos[todo_index].update({
                'completed_at': current_time
            })
        logger.info('Responded with edited todo:')
        logger.info(todos[todo_index])
        return todos[todo_index]

    def delete(self, id):
        """
            Deletes a todo based on ID.
        """
        global todos
        logger.info('Recieved DELETE request for todo ID {}'.format(id))
        new_todos = [t for t in todos if t.get('id') != int(id)]
        if len(new_todos) == len(todos):
            logger.error('Responded with error, no ID match')
            return {'error': 'No todo with id %s' % (id)}

        else:
            todos = new_todos
            logger.info('Responded with success message')
            return {'success': 'Deleted todo with id %s' % (id)}


class TodoListResource(Resource):
    def get(self):
        """
            Returns a list of all todos.
        """
        logger.info('Recieved GET request for all todos')
        logger.info('Responded with all todos:')
        logger.info(todos)
        return todos

    def post(self):
        """
            Creates a new todo based off provided user data. A unique ID
            and certain timestamps are automatically assigned.
        """
        global todos
        global latest_id
        parser.add_argument('name', required=True,
                            help="Name cannot be blank!")
        parser.add_argument('due_date')
        parser.add_argument('completed')
        args = parser.parse_args()
        todo = {
            'id': latest_id + 1,
            'name': args['name'],
            'created_at': time.time(),
            'last_updated_at': None,
            'due_date': args.get('due_date', None),
            'completed': args.get('completed', False),
            'completed_at': None
        }
        logger.info('Recieved POST request for a new todo:')
        logger.info(request.get_json())
        todos.append(todo)
        logger.info('Added todo and responded with newly created todo:')
        logger.info(todo)
        latest_id += 1
        return todo


api.add_resource(TodoResource, '/todo/<string:id>')
api.add_resource(TodoListResource, '/todos')

if __name__ == '__main__':
    app.run(debug=True)
