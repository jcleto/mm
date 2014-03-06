from flask import Flask, request, jsonify
from flask.ext.restful import reqparse, Api,Resource
import json

app = Flask(__name__)
api = Api(app)

progs = []

class MediaManager(Resource):
    progs_id = 0 

    def get(self):
        return progs

    def post(self):
        #  args = parser.parse_args()
        d = json.loads(request.data)
        MediaManager.progs_id += 1
        d['id'] = MediaManager.progs_id
        progs.append(d)
        return progs, 201

#parser = reqparse.RequestParser()
#parser.add_argument('nome', type=str)

api.add_resource(MediaManager, '/mm')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

