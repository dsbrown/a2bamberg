import sys
from mysql.connector import IntegrityError
from pprint import pprint
import s3_upload
import aws_rds
import boto
import json
<<<<<<< HEAD
=======
import os
>>>>>>> 7b9316191a4e2c1d1d5fb16258286592d19ec84e

from flask import flash, Flask, request, jsonify, redirect, render_template, send_from_directory
from flask.ext.restful import Resource, Api, abort, reqparse
from flaskext.uploads import configure_uploads, UploadSet, UploadNotAllowed

# Declare the app
app = Flask(__name__)
api = Api(app)

# Database configuration
rds_url = "assignment2.cqs9bki9xts5.us-east-1.rds.amazonaws.com"
database_name = "assignment2"
table_name = "videos"
username = "root"
password = "sparkles1"
# @ todo move to SQLAlchemy backend --> easy to switch out with DynamoDB
# http://pythonhosted.org/Flask-SQLAlchemy/quickstart.html#a-minimal-application
# Initializes RDS data store. This object can then be used to insert/update/delete video metadata. (Videos are stored in S3)
rds = aws_rds.RDS(
	rds_url=rds_url,
	database_name=database_name, 
	table_name=table_name, 
	username=username, 
	password=password,
	)

# Configure the upload set.
# See http://pythonhosted.org/Flask-Uploads/
app.config['UPLOADED_VIDEOS_DEST'] = '/tmp'
VIDEOS = tuple('mp4 mov mpeg4 avi wmv mpegps flv 3gpp webm'.split())
videos = UploadSet(name='videos', extensions=VIDEOS)
configure_uploads(app, videos)


# Parse request arguments
parser = reqparse.RequestParser()
parser.add_argument('order', type=str, required=False)
parser.add_argument('direction', type=str, required=False)
parser.add_argument('url', type=str, required=False)

# Validate request arguments against these
valid_keys = ['rating', 'timestamp', 'name']
valid_directions = ['asc', 'desc']

# For translating direction to reverse
reverse = {'asc': False, 'desc': True}

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
		vids = rds.get_videos()
		if args['order'] == 'name':
			return sorted(vids, key=lambda vid: vid[args['order']].lower(), reverse=reverse[args['direction']])
		else:
			return sorted(vids, key=lambda vid: vid[args['order']], reverse=reverse[args['direction']])


@app.route('/upload', methods=['GET', 'POST'])
def upload():
	'''Upload a new video.'''
	if request.method == 'POST':
		video = request.files.get('file')
		title = request.form.get('title')
		description = request.form.get('description')
		if not (video and title and description):
			flash("You must fill in all the fields")
		else:
			try:
				filename = videos.save(video)  # flask writes the video to disk
				filepath = os.path.join(app.config['UPLOADED_VIDEOS_DEST'], filename)
			except UploadNotAllowed:
				flash("The upload was not allowed")
				abort(400, message=u"Error saving vehicle: {}".format(str(err)))
			else:
				s3_url = s3_upload.upload(filepath)
				try:
					rds.save_video(name=title, s3_url=s3_url)
					return redirect('/list?order=timestamp&direction=desc')
				except IntegrityError as err:
					flash(u"Duplicate video title. Try again.")
  					return render_template('upload.html')
				    
	elif request.method == 'GET':
		return render_template('upload.html')


class Delete(Resource):
	def get(self):
		args = parser.parse_args()
		# Extract key from URL
		# ...
		# Delete the video
		# boto.s3.bucket.delete_key( ... )
		abort(400, message="DELETE not implemented yet.")


class Rate(Resource):
	def post(self):
		abort(400, message="Rate not implemented yet.")


# The entire python app is hosted under the /api directory, so the full url
# of these will be similar to: /api/list, and /api/upload/success
api.add_resource(List, '/list')
api.add_resource(Delete, '/delete')
api.add_resource(Rate, '/rate')


# # For testing only: for static content
# @app.route('/<path:filename>')
# def send_pic(filename):
# 	return send_from_directory('../www', filename)


# # For testing only: for static content
# @app.route('/<path:filename>')
# def send_pic(filename):
# 	return send_from_directory('../www', filename)


# # For testing only: for static content
# @app.route('/<path:filename>')
# def send_pic(filename):
# 	return send_from_directory('../www', filename)

app.secret_key = ')zq3jg3*3+*32=i$qcdp2(p#k_$!5y_0ridku3i(g&7mql+xqv'

if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)