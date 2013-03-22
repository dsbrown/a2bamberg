import boto.rds
import aws_rds

conn_rds = boto.rds.connect_to_region("us-east-1")

def main():
	#aws_rds.delete_rds(conn_rds)
	aws_rds.create_rds(conn_rds, ec2_group)

if __name__ == '__main__':
	main()