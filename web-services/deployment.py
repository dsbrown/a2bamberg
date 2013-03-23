import boto.rds
import boto.ec2
import aws_rds
import aws_ec2

# Settings
db_name = 'assignment2'
ec2_key_name = 'assignment2'
#db_table = 'movies'
db_sg_name = 'assignment2'
ec2_security_group_name = 'assignment2'
ec2_instance_type = 't1.micro'
ec2_ami = 'ami-3d4ff254'

# Connections
conn_rds = boto.rds.connect_to_region("us-east-1")
conn_ec2 = boto.ec2.connect_to_region("us-east-1")


def main():

	aws_rds.delete_rds(conn_rds, db_name)
	aws_ec2.delete_security_group(conn_ec2, ec2_security_group_name)
	aws_ec2.delete_key_pair(conn_ec2, ec2_key_name)
	aws_ec2.create_key_pair(conn_ec2, ec2_key_name)
	aws_ec2.create_security_group(conn_ec2, ec2_security_group_name)
	aws_rds.create_rds(conn_rds, conn_ec2, ec2_security_group_name, db_name, db_sg_name)
	instance = aws_ec2.create_instance(conn_ec2, ec2_key_name, ec2_security_group_name, ec2_ami)

if __name__ == '__main__':
	main()