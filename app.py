from flask import Flask, request, jsonify
from flask.ext.restful import reqparse, Api,Resource
import json

app = Flask(__name__)
api = Api(app)

progs = []

class MediaManager(Resource):
    def get(self):
        return progs

    def post(self):
        #  args = parser.parse_args()
        js = json.loads(request.data)
        progs.append(js)
        return progs, 201

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

#parser = reqparse.RequestParser()
#parser.add_argument('nome', type=str)

api.add_resource(MediaManager, '/mm')
api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

