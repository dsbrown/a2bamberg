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
from fabtools import require
from fabtools.python import virtualenv

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


# # Removes any existing EC2 or RDS pieces
# def clean():
# 	aws_rds.delete_rds(conn_rds, db_name)
# 	try:
# 		aws_ec2.delete_security_group(conn_ec2, ec2_security_group_name)
# 	except:
# 		print 'Unable to delete security group. Not all instances shut down.  Please manually terminate any EC2 instances that use the security group ' + ec2_security_group_name + '.'
# 	aws_ec2.delete_key_pair(conn_ec2, ec2_key_name)


# Creates RDS database
def create_rds():
	aws_ec2.create_key_pair(conn_ec2, ec2_key_name)
	aws_ec2.create_security_group(conn_ec2, ec2_security_group_name)
	db = aws_rds.create_rds(conn_rds, conn_ec2, ec2_security_group_name, db_name, db_sg_name)
	set_rds_url(db.endpoint)


# Provisions an instance and gets it up and running with static content and the python app
def create_web_server():
	create_instance()
	install_prerequisites()
	start_web_server()


# Creates EC2 instance with permission to access the rds database
def create_instance():
	instance = aws_ec2.create_instance(conn_ec2, ec2_key_name, ec2_instance_type, ec2_security_group_name, ec2_ami)
	set_ec2_url(instance.public_dns_name)


def install_prerequisites():
	if not load_env()['ec2_url']:
		print 'Please run "fab create_instance" before running this command.'
		return

	with settings(host_string = 'ubuntu@' + load_env()['ec2_url'],key_filename = os.path.expanduser('~/.ssh/' + ec2_key_name + '.pem')):
		sudo('apt-get update')

		# install python
		sudo('apt-get -y install nginx')
		sudo('service nginx start')
		sudo('apt-get -y install build-essential python-dev python-setuptools mysql-client git')
		# sudo('easy_install pip') # this is installed when require.python.virtualenv is called

		# # copy python files over into virtual env
		require.python.virtualenv('/home/ubuntu/tube')
		put('../tube/*.py','~/tube')
		put('../tube/*.json','~/tube')
		run('mkdir -p ~/tube/templates')
		put('../tube/templates','~/tube/templates')
		put('../tube/requirements.txt','~/tube/requirements.txt')
		with virtualenv('/home/ubuntu/tube'):
			require.python.requirements('~/tube/requirements.txt')

		# copy static files to static site directory
		run('mkdir -p ~/tube/www')
		with cd('~/tube/www'):
			put('../www','~/tube')


def start_web_server():
	if not load_env()['ec2_url']:
		print 'Please run "fab create_instance" before running this command.'
		return

	print 'Starting server on: ' + load_env()['ec2_url']
	with settings(host_string = 'ubuntu@' + load_env()['ec2_url'],key_filename = os.path.expanduser('~/.ssh/' + ec2_key_name + '.pem')):

		# put web server settings
		put('nginx.conf','/etc/nginx/nginx.conf', use_sudo=True)
		put('sites-available-default','/etc/nginx/sites-available/default', use_sudo=True)
		sudo('rm /etc/nginx/sites-enabled/default')
		sudo('ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default')

		# start web server (stopping and restarting it once to make sure settings take effect)
		sudo('service nginx start')
		sudo('service nginx stop')
		sudo('service nginx start')

		# set permissions on temp folder so files can be uploaded.  In the python code this is 
		# specified as the temporary folder.
		sudo('chmod 777 /tmp')

		# make logging directory and set permissions so it can be written to
		sudo('mkdir -p /var/log/uwsgi') 
		sudo('chmod 777 /var/log/uwsgi')

		# Need to kill old uwsgi in order for it to pick up changes
		try:
			#sudo('ps aux | less')
			#sudo('kill -HUP `cat /var/log/uwsgi/mytube.log`')
			sudo('killall -v /home/ubuntu/tube/bin/uwsgi')
		except:
			pass

		# start new uwsgi
		run('/home/ubuntu/tube/bin/uwsgi -s :8801 --module api --callable app --chdir /home/ubuntu/tube --home /home/ubuntu/tube --daemonize=/var/log/uwsgi/mytube.log')

		# Note: Either a port or a socket file may be used for the --s option.  Socket file requires 
		# that its permissions be set so it is readable by the web server username attempting to access it.

		# run('/home/ubuntu/tube/bin/uwsgi -s /tmp/uwsgi.sock --module api --callable app --chdir /home/ubuntu/tube --home /home/ubuntu/tube')

		# to run as background process, use command: --daemonize=/var/log/uwsgi/mytube.log

		# put('/home/matt/.boto','/home/ubuntu/.boto', use_sudo=True)
		# sudo('chmod 777 /tmp/uwsgi.sock')

		# print 'Server starting on ' + load_env()['ec2_url']

		# with cd('~/tube'):
		# 	run('uwsgi -s /tmp/uwsgi.sock --module api --callable app &')
		# 	# run('uwsgi --http :8035 --static-check=~/tube/www --wsgi-file api.py --callable app --processes 4 --threads 2')


def log():
	with settings(host_string = 'ubuntu@' + load_env()['ec2_url'],key_filename = os.path.expanduser('~/.ssh/' + ec2_key_name + '.pem')):

		# run("ifconfig eth0 | grep inet | awk '{ print $2 }'")
		#sudo('more /var/log/nginx/error.log')
		#sudo('more /var/log/uwsgi/error.log')
		sudo('more /var/log/uwsgi/python.log')
		# sudo('more /etc/nginx/sites-enabled/default')
		# sudo('wget http://ec2-50-19-167-137.compute-1.amazonaws.com/index.html')
		# sudo('netstat -nao | grep 80')
		# sudo("ps aux | egrep '(PID|nginx)'")
		# sudo("/etc/init.d/nginx restart")
		# sudo("kill -QUIT $( cat /var/run/nginx.pid )")


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


# Create a sql database after the RDS instance is live
def create_sql_database():
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