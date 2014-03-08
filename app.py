from flask import Flask, request, jsonify
from flask.ext.restful import reqparse, Api, Resource, abort
from json import loads
from operator import itemgetter

app = Flask(__name__)
api = Api(app)

entities = []


class MediaManagerId(Resource):
    def get(self, type, id):
        el = filter(lambda t: t['id'] == id and t['type'] == type, entities)
        if len(el) == 0:
            abort(404)
        return el[0], 200

    def put(self, type, id):
        el = filter(lambda t: t['id'] == id and t['type'] == type, entities)
        if len(el) == 0:
            abort(404)
        # remove current element
        entities.remove(el[0])
        d = loads(request.data)
        d['id'] = id
        d['type'] = type
        # create new element
        entities.append(d)
        # sort list
        entities.sort(key=itemgetter('id'))
        return d, 201

    def delete(self, type, id):
        el = filter(lambda t: t['id'] == id and t['type'] == type, entities)
        if len(el) == 0:
            abort(404)
        entities.remove(el[0])
        return 204


class MediaManager(Resource):
    entity_id = 0

    def get(self, type):
        el = filter(lambda t: t['type'] == type, entities)
        return el, 200

    def post(self, type):
        d = loads(request.data)
        MediaManager.entity_id += 1
        d['id'] = MediaManager.entity_id
        d['type'] = type
        entities.append(d)
        return d, 201

api.add_resource(MediaManager, '/mm/<string:type>')
api.add_resource(MediaManagerId, '/mm/<string:type>/<int:id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
