import boto

def setup_group(conn, group_name, description=''):

	print('Creating a new security group.')
	conn.create_security_group(name=group_name, description='{g} security group'.format(g=group_name))
	success = conn.authorize_security_group(group_name=group_name, ip_protocol='tcp', 
											from_port=22, to_port=22, cidr_ip='0.0.0.0/0')
	if not success:
		print('Failed to add SSH access.')
	success = conn.authorize_security_group(group_name=group_name, ip_protocol='tcp', 
											from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
	if not success:
		print('Failed to add HTTP access.')
	success = conn.authorize_security_group(group_name=group_name, ip_protocol='udp', 
											from_port=0, to_port=65535, cidr_ip='0.0.0.0/0')
	if not success:
		print('Failed to add UDP access.')