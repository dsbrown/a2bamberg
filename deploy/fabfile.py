import boto.rds
import boto.ec2
import aws_rds
import aws_ec2
from fabric.api import *
from cuisine import *
import pickle
import os.path
import mysql.connector #pip: mysql-connector-python
import exceptions

# Settings
settings_file = os.path.expanduser('~/assignment2-settings.pickle') # pickle settings file where EC2 instance public url and EBS url are stored so they can be used between fabric calls
db_name = 'assignment2' # both name of RDS server and mysql database
db_sg_name = 'assignment2'
ec2_key_name = 'assignment2'
ec2_security_group_name = 'assignment2'
ec2_instance_type = 't1.micro'
ec2_ami = 'ami-3d4ff254'

# Connections
conn_rds = boto.rds.connect_to_region("us-east-1")
conn_ec2 = boto.ec2.connect_to_region("us-east-1")


# Removes any existing EC2 or RDS pieces
def clean():
	aws_rds.delete_rds(conn_rds, db_name)
	try:
		aws_ec2.delete_security_group(conn_ec2, ec2_security_group_name)
	except:
		print 'Unable to delete security group. Not all instances shut down.  Please manually terminate any EC2 instances that use the security group ' + ec2_security_group_name + '.'
	aws_ec2.delete_key_pair(conn_ec2, ec2_key_name)


# Creates RDS database
def create_rds():
	aws_ec2.create_key_pair(conn_ec2, ec2_key_name)
	aws_ec2.create_security_group(conn_ec2, ec2_security_group_name)
	db = aws_rds.create_rds(conn_rds, conn_ec2, ec2_security_group_name, db_name, db_sg_name)
	set_rds_url(db.endpoint)


# Creates EC2 instance with permission to access the rds database
def create_instance():
	instance = aws_ec2.create_instance(conn_ec2, ec2_key_name, ec2_instance_type, ec2_security_group_name, ec2_ami)
	set_ec2_url(instance.public_dns_name)


def install_prerequisites():
	with settings(host_string = 'ubuntu@' + load_env()['ec2_url'],key_filename = os.path.expanduser('~/.ssh/' + ec2_key_name + '.pem')):
		sudo('apt-get update')
		sudo('apt-get -y install build-essential python-dev python-setuptools mysql-client')
		sudo('easy_install pip')
		sudo('pip install uwsgi') # this actually does have to be run outside of a virtualenv, so the config files are installed to system locations


def set_rds_url(rds_url):
	env = load_env()
	env['rds_url'] = rds_url
	save_env(env)


def set_ec2_url(ec2_url):
	env = load_env()
	env['ec2_url'] = ec2_url
	save_env(env)


def load_env():
	if os.path.exists(settings_file):
		ret = pickle.load(open(settings_file, "rb"))
		print 'Loaded settings from file: '
		print ret
		return ret
	else:
		print 'No settings file found. Loading empty settings.'
		return {}


def save_env(env):
	print 'Saved settings: '
	print env
	pickle.dump(env, open(settings_file, "wb"))


# Test creating a sql database
def test_sql():
	if (load_env()['rds_url'] == None):
		raise exception.Exception('Error: "rds_url" has not yet been set. Please run "fab create_rds" to create the RDS database.')

	local("mysql -h{url} -uroot -psparkles1 -e 'create database if not exists {db_name}'".format(url=load_env()['rds_url'],db_name=db_name))
	# connect to database
	conn = mysql.connector.connect(user='root', password='sparkles1', host=load_env()['rds_url'], database=db_name)

	movies_table_sql = """CREATE TABLE IF NOT EXISTS videos (
							name varchar(50) NOT NULL PRIMARY KEY,
							timestamp datetime NOT NULL,
							rating double,
							num_ratings int,
							s3_url varchar(400),
							streaming_url varchar(400))
						"""
	cursor = conn.cursor()

	# deletes table if exists
	cursor.execute("DROP TABLE IF EXISTS videos")

	# creates table
	cursor.execute(movies_table_sql)

	# Add data
	cursor.execute("INSERT INTO videos(name, timestamp, rating, num_ratings) VALUES('Test Vid 1', NOW(), 0.0, 0)")
	cursor.execute("INSERT INTO videos(name, timestamp, rating, num_ratings) VALUES('Test Vid 2', NOW(), 0.0, 0)")
	cursor.execute("INSERT INTO videos(name, timestamp, rating, num_ratings) VALUES('Test Vid 3', NOW(), 0.0, 0)")
	cursor.execute("INSERT INTO videos(name, timestamp, rating, num_ratings) VALUES('Test Vid 4', NOW(), 0.0, 0)")
	cursor.execute("SELECT * FROM videos")

	# print out all data in the table
	for row in cursor.fetchall():
		print row

	conn.commit() # commit() necessary, or changes are not saved
	conn.close()



# EXAMPLE FABRIC/CUSINE CODE
# @hosts('host1')
# def clean_and_upload():
#     local('find assets/ -name "*.DS_Store" -exec rm '{}' \;')
#     local('tar czf /tmp/assets.tgz assets/')
#     put('/tmp/assets.tgz', '/tmp/assets.tgz')
#     with cd('/var/www/myapp/'):
#         run('tar xzf /tmp/assets.tgz')