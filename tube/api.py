# See http://httpstatus.es/ for HTTP response codes
from pprint import pprint
from flask import Flask, request, jsonify, redirect
from flask.ext.restful import Resource, Api, abort, reqparse
import boto

app = Flask(__name__)
api = Api(app)

vids = []
def save_video(name, s3_url):
	vids.append({
		'n': len(vids) + 1,
		'name': name,
		'timestamp': 'NEEDS_TIMESTAMP',
		'rating': 0,
		'num_ratings': 0,
		's3_url': s3_url,
		'streaming_url': 'NEEDS_CLOUDFRONT'
		})

# Test data
save_video('kitten-surprise.mp4', 'https://s3.amazonaws.com/chrishaum.bucket/uploads/kitten-surprise.mp4')
save_video('talking-cats', 'https://s3.amazonaws.com/chrishaum.bucket/uploads/talking-cats.mp4')

# Parse request arguments
parser = reqparse.RequestParser()
parser.add_argument('order', type=str, required=False)
parser.add_argument('direction', type=str, required=False)
parser.add_argument('url', type=str, required=False)

# Validate request arguments against these
valid_keys = ['rating', 'timestamp', 'name']
valid_directions = ['ascending', 'descending']

# For translating direction to reverse
reverse = {'ascending': False, 'descending': True}

def validate_list_args(args):
	'''Validate request arguments'''
	if args['order'] not in valid_keys:
		abort(400, message=u"Invalid 'order' value: {}. Valid values: {}".format(args['order'], valid_keys))
	if args['direction'] not in valid_directions:
		abort(400, message=u"Invalid 'direction' value: {}. Valid values: {}".format(args['direction'], valid_directions))


class List(Resource):
	def get(self):
		args = parser.parse_args()
		validate_list_args(args)
		return sorted(vids, key=lambda vid: vid[args['order']], reverse=reverse[args['direction']])


class Delete(Resource):
	def get(self):
		args = parser.parse_args()

		# Extract key from URL
		# ...

		# Delete the video
		# boto.s3.bucket.delete_key( ... )

		abort(402, message="Delete not implemented yet.")
		return jsonify({'deleted=True, '})


class Rate(Resource):
	def post(self):
		pass

api.add_resource(List, '/api/list')
api.add_resource(Delete, '/api/delete')
api.add_resource(Rate, '/api/rate')

@app.route('/upload/success')
def upload_success():
	bucket = request.args.get('bucket','')
	key = request.args.get('key','')
	url = "https://s3.amazonaws.com/{}/{}".format(bucket, key)
	save_video(name=key, s3_url=url)
	return redirect('/api/list?order=rating&direction=descending')


if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)