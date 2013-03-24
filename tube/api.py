# See http://httpstatus.es/ for HTTP response codes
from pprint import pprint
from flask import Flask, request
from flask.ext.restful import Resource, Api, abort, reqparse

app = Flask(__name__)
api = Api(app)

# Test data
vids = []
for i in range(3):
	vids.append({	
	'name': 'vid{}'.format(i),
	'timestamp': 10 - i,
	'rating': i,
	'num_ratings': 22,
	's3_url': 'http://s3....',
	'streaming_url': 'http://cloudfront...',
})

# Parse request arguments
parser = reqparse.RequestParser()
parser.add_argument('order', type=str, required=False)
parser.add_argument('direction', type=str, required=False)

# Validate request arguments against these
valid_keys = ['rating', 'timestamp', 'name']
valid_directions = ['ascending', 'descending']

# For translating direction to reverse
reverse = {'ascending': False, 'descending': True}

def validate_args(args):
	'''Validate request arguments'''
	if args['order'] not in valid_keys:
		abort(400, message=u"Invalid 'order' value: '{}'. Valid values: {}".format(args['order'], valid_keys))
	if args['direction'] not in valid_directions:
		abort(400, message=u"Invalid 'direction' value: {}. Valid values: {}".format(args['direction'], valid_directions))


class List(Resource):
	def get(self):
		args = parser.parse_args()
		validate_args(args)
		return sorted(vids, key=lambda vid: vid[args['order']], reverse=reverse[args['direction']])


class Upload(Resource):
	def post(self):
		pass

class Delete(Resource):
	def post(self):
		pass

class Rate(Resource):
	def post(self):
		pass

api.add_resource(List, '/api/list')
api.add_resource(Upload, '/api/upload')
api.add_resource(Delete, '/api/delete')
api.add_resource(Rate, '/api/rate')

if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)