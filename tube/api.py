# See http://httpstatus.es/ for HTTP response codes
import sys
from pprint import pprint
import s3_upload
import aws_rds
import boto

from flask import Flask, request, jsonify, redirect, send_from_directory, flash
from flask.ext.restful import Resource, Api, abort, reqparse
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import delete, init, save, Upload

config = json.loads(open('config.json','r').read())


app = Flask(__name__)
api = Api(app)

# @ todo move to SQLAlchemy backend --> easy to switch out with DynamoDB
# http://pythonhosted.org/Flask-SQLAlchemy/quickstart.html#a-minimal-application
# Initializes RDS data store. This object can then be used to insert/update/delete video metadata. (Videos are stored in S3)
rds = aws_rds.RDS(
	rds_url=config['rds_url'],
	database_name=config['database_name'], 
	table_name=config['table_name'], 
	username=config['username'], 
	password=config['password'],
	)

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



VIDEOS = tuple('mp4 mov mpeg4 avi wmv mpegps flv 3gpp webm'.split())
@app.route('/upload', methods=['GET', 'POST'])
def new():
	video_set = UploadSet(name='videos', extensions=VIDEOS)
	if request.method == 'POST':
        video = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')
        if not (video and title and description):
            flash("You must fill in all the fields")
        else:
            try:
                filename = video_set.save(video)  # flask writes the video to disk
            except UploadNotAllowed:
                flash("The upload was not allowed")
            else:
                vid = Video(title=title, description=description, filename=filename)
                vid.id = unique_id()
                # vid.store()
                rds.save_video(name=args['name'], s3_url=s3_url)
                flash("Video successfully saved.")
                return to_index()
    # return render_template('upload.html')
    return redirect('/list?order=rating&direction=desc')


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
api.add_resource(Upload, '/upload')
api.add_resource(Delete, '/delete')
api.add_resource(Rate, '/rate')


@app.route('/upload/success')
def upload_success():
	bucket = request.args.get('bucket','')
	key = request.args.get('key','')
	s3_url = "https://s3.amazonaws.com/{}/{}".format(bucket, key)
	try:
		rds.save_video(name=args['name'], s3_url=s3_url)
	except Exception, err:
		abort(400, message=u"Error saving vehicle: {}".format(str(err)))

	return redirect('/list?order=rating&direction=desc')


# # For testing only: for static content
# @app.route('/<path:filename>')
# def send_pic(filename):
# 	return send_from_directory('../www', filename)


# # For testing only: for static content
# @app.route('/<path:filename>')
# def send_pic(filename):
# 	return send_from_directory('../www', filename)


if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)