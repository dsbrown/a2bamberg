# See http://httpstatus.es/ for HTTP response codes
import sys
from pprint import pprint
from flask import Flask, request, jsonify, redirect
from flask.ext.restful import Resource, Api, abort, reqparse
import aws_rds

app = Flask(__name__)
api = Api(app)

# # Now implemented in aws_rds class
# vids = []
# def save_video(name, s3_url):
# 	vids.append({
# 		'n': len(vids) + 1,
# 		'name': name,
# 		'timestamp': 'NEEDS_TIMESTAMP',
# 		'rating': 0,
# 		'num_ratings': 0,
# 		's3_url': s3_url,
# 		'streaming_url': 'NEEDS_CLOUDFRONT'
# 		})
#
# save_video('kitten-surprise.mp4', 'https://s3.amazonaws.com/chrishaum.bucket/uploads/kitten-surprise.mp4')
# save_video('talking-cats', 'https://s3.amazonaws.com/chrishaum.bucket/uploads/talking-cats.mp4')


# Initializes RDS data store. This object can then be used to insert/update/delete videos.
rds = aws_rds.RDS(
	rds_url='assignment2.cqs9bki9xts5.us-east-1.rds.amazonaws.com', # just hard-coded the name of the server i've been using--put into persistant settings file? - Matt
	database_name='assignment2', 
	table_name='videos', 
	username='root', 
	password='sparkles1'
	)

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
		abort(400, message=u"Invalid 'order' value: {}. Valid values: {}".format(args['order'], valid_keys))
	if args['direction'] not in valid_directions:
		abort(400, message=u"Invalid 'direction' value: {}. Valid values: {}".format(args['direction'], valid_directions))


class List(Resource):
	def get(self):
		args = parser.parse_args()
		validate_args(args)
		vids = rds.get_videos()
		return sorted(vids, key=lambda vid: vid[args['order']], reverse=reverse[args['direction']])


class Upload(Resource):
	def post(self):
		args = parser.parse_args()
		try:
			rds.save_video(
				name=args['name'],
				s3_url='test'
				)
		except Exception, err:
			abort(400, message=u"Error saving vehicle: {}".format(str(err)))
		return 'Vehicle added'


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

@app.route('/upload/success')
def upload_success():
	bucket = request.args.get('bucket','')
	key = request.args.get('key','')
	url = "https://s3.amazonaws.com/{}/{}".format(bucket, key)
	save_video(name=key, s3_url=url)
	return redirect('/api/list?order=rating&direction=descending')


if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)