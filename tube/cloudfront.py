import boto
import json
from boto.cloudfront import CloudFrontConnection
from boto.cloudfront.origin import S3Origin

config = json.loads(open('config.json','r').read().decode('utf-8'))

def distribute(s3_url):
	c = CloudFrontConnection(config['aws-access-key'].strip(), config['aws-secret-access-key'].strip())
	rs = c.get_all_distributions()
	try:
		ds = rs[0]
		distro = ds.get_distribution()
	except IndexError:
		origin = '{}.s3.amazonaws.com'.format(config['aws-bucket-name'])
		s3_origin = S3Origin(dns_name=origin)
		distro = c.create_distribution(origin=s3_origin, enabled=True, comment="Videos")
	key_name = s3_url.split('/')[-1]
	return 'http://{}/{}'.format(distro.domain_name, key_name)