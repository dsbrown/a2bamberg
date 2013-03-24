# Methods that interact with Amazon RDS
from fabric.api import *
import mysql.connector #pip: mysql-connector-python

class RDS:
	def __init__(self, rds_url, database_name, table_name, username, password):
		self.rds_url = rds_url
		self.database_name = database_name
		self.table_name = table_name
		self.username = username
		self.password = password


	movies_table_sql = """CREATE TABLE IF NOT EXISTS videos (
							name varchar(50) NOT NULL PRIMARY KEY,
							timestamp datetime NOT NULL,
							rating double,
							num_ratings int,
							s3_url varchar(400),
							streaming_url varchar(400))
						"""

	def get_conn(self):
		# connect to db
		return mysql.connector.connect(user=self.username, password=self.password, host=self.rds_url, database=self.database_name)


	def save_video(self, name, s3_url):
		self.ensure_db_exists()
		conn = self.get_conn()
		cursor = conn.cursor()

		# Add data
		sql = """INSERT INTO {table_name}(name, timestamp, rating, num_ratings, s3_url, streaming_url) 
					VALUES(%(name)s, NOW(), 0, 0, %(s3_url)s, %(streaming_url)s)""".format(table_name=self.table_name)
		video_data = {
			'name': name,
			's3_url': s3_url,
			'streaming_url': 'NEEDS_CLOUDFRONT'
		}

		cursor.execute(sql, video_data)
		conn.commit() # commit() necessary, or changes are not saved
		conn.close()

	def get_videos(self):
		self.ensure_db_exists()
		conn = self.get_conn()
		cursor = conn.cursor()
		cursor.execute("SELECT name, timestamp, rating, num_ratings, s3_url, streaming_url FROM videos")
		rows = cursor.fetchall()
		videos = []
		for (name, timestamp, rating, num_ratings, s3_url, streaming_url) in rows:
			print (name, timestamp, rating, num_ratings, s3_url, streaming_url)
			videos.append({
				"name": name,
				"timestamp": timestamp.isoformat(),
				"rating": rating,
				"num_ratings": num_ratings,
				"s3_url": s3_url,
				"streaming_url": streaming_url
				})

		conn.close()
		return videos


	def ensure_db_exists(self):
		local("mysql -h{url} -u{username} -p{password} -e 'create database if not exists {database_name}'"
			.format(
				url=self.rds_url,
				username=self.username,
				password=self.password,
				database_name=self.database_name,
				))
		
		# connect to database
		conn = self.get_conn()
		cursor = conn.cursor()

		# creates table
		cursor.execute(self.movies_table_sql)

		conn.commit() # commit() necessary, or changes are not saved
		conn.close()

	def recreate_table(self):
		conn = self.get_conn();
		cursor = conn.cursor()

		# deletes table if exists
		cursor.execute("DROP TABLE IF EXISTS {table_name}".format(table_name=self.table_name))

		# creates table
		cursor.execute(movies_table_sql)

		conn.commit() # commit() necessary, or changes are not saved
		conn.close()