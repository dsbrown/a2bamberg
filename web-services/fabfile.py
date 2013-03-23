import boto.rds
import boto.ec2
import aws_rds
import aws_ec2
import fabric
import cuisine
import pickle
import os.path

# Settings
settings_file = os.path.expanduser('~/assignment2-settings.pickle')
db_name = 'assignment2'
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


# Creates RDS database and EC2 instance that is priviledged to access it
def create_rds():
	aws_ec2.create_key_pair(conn_ec2, ec2_key_name)
	aws_ec2.create_security_group(conn_ec2, ec2_security_group_name)
	db = aws_rds.create_rds(conn_rds, conn_ec2, ec2_security_group_name, db_name, db_sg_name)
	set_rds_url(db.enpoint)
	instance = aws_ec2.create_instance(conn_ec2, ec2_key_name, ec2_instance_type, ec2_security_group_name, ec2_ami)
	set_ec2_url(instance.public_dns_name)


def set_rds_url(rds_url):
	env = load_env()
	env['rds_url'] = rds_url
	save_env(env)


def set_ec2_url(ec2_url):
	env = load_env()
	env['ec2_url'] = ec2_url
	save_env(env)


#sudo apt-get update
#sudo apt-get install python-dev python-setuptools mysql-client
#sudo easy_install pip


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