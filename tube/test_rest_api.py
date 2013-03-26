from nose.tools import *
from fabric.api import env, local, run
from requests import put, get

def test_404():
	r = get('http://localhost:5000/FAIL')
	eq_(r.status_code, 404)


def list(order, direction):
	r = get('http://localhost:5000/api/list', params={'direction':direction, 'order': order})
	return r.json()


def test_list():
	j = list('name','ascending')
	eq_(j[0]['name'],'vid0')

	j = list('timestamp','descending')
	assert j[0]['timestamp'] > j[1]['timestamp']

	j = list('rating','ascending')
	assert j[0]['rating'] < j[1]['rating']


def delete(url):
	r = get('http://localhost:5000/api/delete?url={}'.format(url))
	return r.json()


def test_delete():
	j = delete('talking-cats.mp4')
	url = 'https://s3.amazonaws.com/chrishaum.bucket/uploads/{}'.format(key)
	assert r.json()['deleted']