import boto
import json
import os

config = json.loads(open('config.json','r').read().decode('utf-8'))

def ensure_bucket():
	
	connection = boto.connect_s3(config['aws-access-key'].strip(), config['aws-secret-access-key'].strip())  # @todo security vulnerability

	try:
		buckets = connection.get_all_buckets()
	except:
		print('Invalid login credentials.')
		return
	aws_bucket_name = config['aws-bucket-name']

	if aws_bucket_name not in [b.name for b in buckets]:
		try:
			aws_bucket = connection.create_bucket(aws_bucket_name, policy='public-read')
		except boto.exception.S3CreateError, e:
			print('Bucket with name {} already in use.'.format(aws_bucket_name))
			return
	else:
		for b in buckets:
			if b.name == aws_bucket_name:
				aws_bucket = b
	return aws_bucket

def upload(the_file):
	aws_bucket = ensure_bucket()

	# Upload the file
	k = boto.s3.key.Key(aws_bucket)
	k.key = os.path.basename(the_file)
	k.set_contents_from_filename(the_file, policy='public-read')
	url = '/'.join((config['aws-bucket-website'], config['aws-bucket-name'], k.key))
	return url

def delete(key_name):
	aws_bucket = ensure_bucket()
	aws_bucket.delete_key(key_name=key_name)