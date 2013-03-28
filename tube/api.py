import sys
from mysql.connector import IntegrityError
from pprint import pprint
import s3
import aws_rds
import boto
import json
import os
import exceptions

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


class List(Resource):
	def get(self, id=None):
		vids = rds.get_videos()
		if not id:
			return sorted(vids, key=lambda vid: vid['timestamp'], reverse=True)
		else:
			for vid in vids:
				if vid['id'] == id:
					return vid
		abort(404, "That video does not exist.")


@app.route('/api/upload', methods=['POST', 'GET'])
def upload():
	'''Upload a new video.'''
	if request.method == 'POST':
		video = request.files.get('file')
		name = request.form.get('name')
		if not (video and name):
			flash("You must fill in all the fields")
			return render_template('upload.html')
		else:
			try:
				filename = videos.save(video)  # flask writes the video to disk
				filepath = os.path.join(app.config['UPLOADED_VIDEOS_DEST'], filename)
			except UploadNotAllowed:
				flash("Only videos are allowed.")
				return render_template('upload.html')
			else:
				s3_url = s3.upload(filepath)
				try:
					rds.save_video(name=name, s3_url=s3_url)
					return redirect('/index.html')
				except IntegrityError as err:
					flash("Duplicate video title. Try again.")
					return render_template('upload.html')
				    
	elif request.method == 'GET':
		return redirect('/upload.html')


class Rate(Resource):
	def post(self):
		# Parse request arguments
		parser = reqparse.RequestParser()
		parser.add_argument('id', type=int, required=True)
		parser.add_argument('rating', type=int, required=True)
		args = parser.parse_args()
		new_rating = rds.rate_video(args['id'],args['rating'])
		return { "new_rating": new_rating }


class Delete(Resource):
	def post(self, id):
		vid = rds.get_videos(specific_id=id)[0]
		rds.delete_video(video_id=id)
		key_name = vid['s3_url'].split('/')[-1]
		s3.delete(key_name=key_name)
		return render_template('/index.html')


# The entire python app is hosted under the /api directory, so the full url
# of these will be similar to: /api/list, and /api/upload/success
api.add_resource(List, '/api/list', '/api/list/', '/api/list/<int:id>')
api.add_resource(Delete, '/api/delete/<int:id>')
api.add_resource(Rate, '/api/rate')

# For testing only: for static content
@app.route('/<path:filename>')
def send_pic(filename):
	return send_from_directory('../www', filename)

app.secret_key = ')zq3jg3*3+*32=i$qcdp2(p#k_$!5y_0ridku3i(g&7mql+xqv'

if __name__ == '__main__':
	app.run('0.0.0.0', debug=True, port=5000)