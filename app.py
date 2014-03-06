from flask import Flask, request, jsonify
from flask.ext.restful import reqparse, Api,Resource
import json

app = Flask(__name__)
api = Api(app)

progs = []

class MediaManager(Resource):
    def __init__(self):
             self.progs_id = 0 
             super(MediaManager, self).__init__()

    def get(self):
        return progs

    def post(self):
        #  args = parser.parse_args()
        d = json.loads(request.data)
        self.progs_id = self.progs_id + 21
        print self.progs_id
        d['id'] = self.progs_id
        progs.append(d)
        return progs, 201

#parser = reqparse.RequestParser()
#parser.add_argument('nome', type=str)

api.add_resource(MediaManager, '/mm')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

