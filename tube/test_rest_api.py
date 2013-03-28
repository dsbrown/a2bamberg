from nose.tools import *
from fabric.api import env, local, run
import requests
from werkzeug import secure_filename
import api
import json
import uuid
import s3


api.app.config['TESTING'] = True
app = api.app.test_client()

def test_404():
	r = app.get('SHOULD_404')
	eq_(r.status_code, 404)


def test_list():
	r = app.get('/list')
	eq_(r.status_code, 200)
	eq_(r.content_type, 'application/json')


def video_in_list(the_list, **kwargs):
	r = False
	for vid in the_list:
		vid_list = []
		for name, value in kwargs.items():
			try:
				vid_list.append(bool(vid[name] == value))
			except KeyError:
				pass
		if all(vid_list):
			r = vid
	return r


def list_all():
	return json.loads(app.get('/list').data)

def most_recent_video():
	return sorted( list_all(), key= lambda vid: vid['timestamp'], reverse=True)[0]

def test_s3_delete():
	vid = most_recent_video()
	s3_url = vid['s3_url']
	key_name = vid['name']
	eq_(requests.get(s3_url).status_code, 200)
	r = app.get('/delete/{}'.format(key_name))
	eq_(requests.get(s3_url).status_code, 403)