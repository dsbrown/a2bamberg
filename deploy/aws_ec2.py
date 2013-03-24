import boto
import os.path
from time import sleep

def create_security_group(conn, security_group_name, description=''):

	print('Creating a new security group.')
	sg = conn.create_security_group(name=security_group_name, description='{g} security group'.format(g=security_group_name))
	# success = conn.authorize_security_group(group_name=security_group_name, ip_protocol='tcp', 
	# 										from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
	# if not success:
	# 	print('Failed to add SSH access.')
	# success = conn.authorize_security_group(group_name=security_group_name, ip_protocol='tcp', 
	# 										from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
	# if not success:
	# 	print('Failed to add HTTP access.')

	success = conn.authorize_security_group(group_name=security_group_name, ip_protocol='tcp', 
											from_port=0, to_port=65535, cidr_ip='0.0.0.0/0')
	if not success:
		print('Failed to add UDP access.')

	success = conn.authorize_security_group(group_name=security_group_name, ip_protocol='udp', 
											from_port=0, to_port=65535, cidr_ip='0.0.0.0/0')
	if not success:
		print('Failed to add UDP access.')

	return sg


def delete_security_group(conn, security_group_name):
	# Delete security groups
	groups = conn.get_all_security_groups()
	group_names = [x.__str__().split(':')[1] for x in groups if security_group_name in x.__str__()]
	for g in group_names:
		conn.delete_security_group(name=g)
		print('deleted security group: {g}'.format(g=g))


# Make sure that key exist on local machine and Amazon machine.  
# If either does not, it deletes and recreates.
def create_key_pair(conn, key_pair_name):
	new_key = conn.create_key_pair(key_pair_name)
	new_key.save(os.path.expanduser('~/.ssh'))
	return new_key


def delete_key_pair(conn, key_pair_name):
	# Delete key pairs
	pairs = conn.get_all_key_pairs()
	key_names = [x.__str__().split(':')[1] for x in pairs if key_pair_name in x.__str__()]
	for k in key_names:
		conn.delete_key_pair(k)
		file_path = os.path.expanduser('~/.ssh/{key_name}.pem'.format(key_name=k))
		if os.path.exists(file_path):
			os.remove(file_path)
		print('deleted key: {k}'.format(k=k))

# Creates a new instance.  Assumes that the SSH Key and Security group exist already.
def create_instance(conn, key_pair_name, instance_type, security_group_name, ami):
	reservation = conn.run_instances(ami,
		key_name=key_pair_name,
		instance_type=instance_type,
		security_groups=[security_group_name])

	print "New instance starting. Reservation Id:", reservation.id
	newInstance = reservation.instances[0]
	
	# Wait for instance to be provisioned
	while (newInstance.state != "running"):
		print "\tWaiting for instance to be provisioned. Request status is " + newInstance.state + "..."
		sleep(5)
		newInstance.update()
	print "Instance is provisioned."
	print "\tIP Address: " + newInstance.ip_address
	print "\tPublic DNS: " + newInstance.public_dns_name

	# Alert user that instance is still not ready for use--it has to boot
	print "Waiting for instance to boot to before connecting... (It will take appx. 50 seconds)... Please wait..."
	sleep(50)
	print "Instance booted."

	return newInstance