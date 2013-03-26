from nose.tools import *
from fabric.api import env, local, run
from requests import put, get

def test_404():
	r = get('http://localhost:5000/FAIL')
	eq_(r.status_code, 404)


def list(order, direction):
	r = get('http://localhost:5000/list', params={'direction':direction, 'order': order})
	return r.json()

def test_list():
	j = list('name','asc')
	eq_(j[0]['name'],'kitten-surprise.mp4')
	j = list('timestamp','desc')
	assert j[0]['timestamp'] >= j[1]['timestamp']
	j = list('rating','asc')
	assert j[0]['rating'] <= j[1]['rating']

def test_s3_upload():
	r = put('http://localhost:5000/upload')  # @todo
	eq_(r.status_code, 301)

@with_setup(test_s3_upload)
def test_s3_delete():
	key = 'talking-cats.mp4'
	s3_url = 'https://s3.amazonaws.com/chrishaum.bucket/uploads/{}'.format(key)
	delete_endpoint = 'http://localhost:5000/delete?url={}'.format(s3_url)
	eq_(get(s3_url).status_code, 200)
	r = get(delete_endpoint)
	# eq_(r.json()['deleted'], 'True')
	eq_(get(s3_url).status_code, 404)
	

@nottest
def test_upload_success():
	r = get('http://localhost:5000/upload/success')
	eq_(r.status_code, 404)