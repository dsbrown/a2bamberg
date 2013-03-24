# See http://httpstatus.es/ for HTTP response codes

from flask import Flask, request
from flask.ext.restful import Resource, Api, abort, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('vin', type=str, required=True, help='vin cannot be blank')

# Dummy vehicles object
vehicles = {'123': {'vin':'123', 'vehicle_images': ['img_url_1','img_url_2']}}

# We'll populate this with images as they are uploaded
# @todo issue: manage files that are uploaded to this host but not yet to S3
staged_image_urls = {}

def abort_if_vin_doesnt_exist(args):
	if 'vin' not in args:
		abort(400, message=u"Request requires a 'vin' argument")
	if args['vin'] not in vehicles:
		abort(404, message="Vehicle {} does not exist".format(args['vin']))

class ListVehicles(Resource):
	def get(self):
		return vehicles

class ListImages(Resource):
	def get(self):
		args = parser.parse_args()
		abort_if_vin_doesnt_exist(args)
		return {'vehicle_images': vehicles[args['vin']]['vehicle_images']}

class SaveImage(Resource):
	def post(self):
		abort(404, message="Not implemented yet")

class SaveVehicle(Resource):
	def post(self):
		abort(404, message="Not implemented yet")


api.add_resource(ListVehicles, '/api/list-vehicles')
api.add_resource(ListImages, '/api/list-images')
api.add_resource(SaveImage, '/api/save-image')
api.add_resource(SaveVehicle, '/api/save-vehicle')

if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)