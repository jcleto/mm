from flask import Flask, request, jsonify
from flask.ext.restful import reqparse, Api,Resource
from json import loads

app = Flask(__name__)
api = Api(app)

progs = []
brands = []

class MediaManager(Resource):
    progs_id = 0
    brand_id = 0

    def get(self, type):
        if type == 'program':
            return progs
        if type == 'brand':
            return brands
        return 404

    def post(self, type):
        #  args = parser.parse_args()
        d = loads(request.data)
        d['type'] = type
        if type == 'brand':
            MediaManager.brand_id += 1
            d['id'] = MediaManager.brand_id
            brands.append(d)
            return progs, 201
        if type == 'program':
            MediaManager.progs_id += 1
            d['id'] = MediaManager.progs_id
            progs.append(d)
            return progs, 201
        return 400

#parser = reqparse.RequestParser()
#parser.add_argument('nome', type=str)

api.add_resource(MediaManager, '/mm/<string:type>')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

