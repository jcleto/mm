from flask import Flask, request  # , jsonify, redirect
from flask.ext.restful import Api, Resource, abort  # , reqparse
from json import loads
from operator import itemgetter

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)

entities = []


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('no server running')
    func()

#@app.before_request
#def remove_trailing_slash():
#    if request.path != '/' and request.path.endswith('/'):
#        return redirect(request.path[:-1])


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'shuting down server'


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


api.add_resource(MediaManager, '/api/types/<string:type>/entities')
api.add_resource(MediaManagerId, '/api/types/<string:type>/entities/<int:id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=False)
