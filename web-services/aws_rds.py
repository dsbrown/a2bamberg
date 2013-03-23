import sys
import boto.rds
from boto.ec2.securitygroup import SecurityGroup
from time import sleep


# Main function to create a RDS instance, authorize it with an EC2 group, the
# return the endpoint that it can be reached at. Endpoint can be used like
# a normal MySQL database from the authorized EC2 instance.
def create_rds(conn, conn_ec2, ec2_security_group_name, db_name, db_sg_name):
	rds_db = create_rds_db(conn, db_name)
	create_rds_security_group(conn, conn_ec2, rds_db, ec2_security_group_name, db_sg_name)
	return db.endpoint


def create_rds_db(conn, db_name):
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


def create_rds_security_group(conn, conn_ec2, rds_db, ec2_security_group_name, db_sg_name):
	sgs = [i for i in conn.get_all_dbsecurity_groups() if i.name == db_sg_name]
	if len(sgs) == 0:
		sg = conn.create_dbsecurity_group(db_sg_name, db_sg_name)
		ec2sg = conn_ec2.get_all_security_groups(groupnames=[ec2_security_group_name])[0]
		sg.authorize(ec2_group=ec2sg)
	else:
		sg = sgs[0]

	rds_db.modify(security_groups=[sg])
	return sg


def delete_rds(conn, db_name):
	# Delete any RDS instances that exist
	for i in [i for i in conn.get_all_dbinstances() if i.id == db_name and i.status != 'deleting']:
		conn.delete_dbinstance(id=i.id,skip_final_snapshot=True)

	# Wait to return until all matching instances are gone
	while len([i for i in conn.get_all_dbinstances() if i.id == db_name]) > 0:
		print 'Waiting for RDS instance to delete...'
		sleep(5)

	print 'All RDS db instances have been deleted.'