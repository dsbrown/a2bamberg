import sys
import boto.rds
import boto.ec2.securitygroup.SecurityGroup
from time import sleep

db_name = 'db-assignment2'
db_table = 'movies'
db_sg_name = 'web_servers'


# Main function to create a RDS instance, authorize it with an EC2 group, the
# return the endpoint that it can be reached at. Endpoint can be used like
# a normal MySQL database from the authorized EC2 instance.
def create_rds(conn, ec2_group):
	if not isinstance(ec2_group, boto.ec2.securitygroup.SecurityGroup):
		raise Exception('EC2 group is not an object of type "ec2.securitygroup.SecurityGroup" as expected.')
	db = create_rds_db(conn)
	create_rds_security_group(conn, rds_db, ec2_group)
	return db.endpoint


def create_rds_db(conn):
	print 'Creating RDS database and table...'
	
	# only create database if it does not already exist
	dbs = [i for i in conn.get_all_dbinstances() if i.id == db_name]
	if len(dbs) == 0:
		db = conn.create_dbinstance(db_name, 5, 'db.t1.micro', 'root', 'sparkles1')
		print 'Waiting for RDS database to initialize...'
		while db.status != 'available':
			sleep(5)
			db = conn.get_all_dbinstances(db_name)[0]
			print db.status
	else:
		db = dbs[0]

	print 'RDS database created'
	return db


def create_rds_security_group(conn, rds_db, ec2_group):
	sgs = [i for i in conn.get_all_dbsecurity_groups() if i.id == db_sg_name]
	if len(sgs) == 0:
		sg = conn.create_dbsecurity_group(db_sg_name, 'Web front-ends')
		sg.authorize(ec2_group=ec2_group)
	else:
		sg = sgs[0]

	rds_db.modify(security_groups=[sg])


def delete_rds(conn):
	# Delete any RDS instances that exist
	for i in [i for i in conn.get_all_dbinstances() if i.id == db_name and i.status != 'deleting']:
		conn.delete_dbinstance(id=i.id,skip_final_snapshot=True)

	# Wait to return until all matching instances are gone
	while len([i for i in conn.get_all_dbinstances() if i.id == db_name]) > 0:
		print 'Waiting for RDS instance to delete...'
		sleep(5)

	print 'All RDS db instances have been deleted.'