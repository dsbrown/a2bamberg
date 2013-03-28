# Methods that interact with Amazon RDS
from fabric.api import *
import mysql.connector #pip: mysql-connector-python
import exceptions

class RDS:
	def __init__(self, rds_url, database_name, table_name, username, password):
		self.rds_url = rds_url
		self.database_name = database_name
		self.table_name = table_name
		self.username = username
		self.password = password
		self.ensure_db_exists()


	movies_table_sql = """CREATE TABLE IF NOT EXISTS videos (
							id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
							name varchar(50) NOT NULL,
							timestamp datetime NOT NULL,
							rating double,
							num_ratings int,
							s3_url varchar(1000),
							streaming_url varchar(1000),
							UNIQUE(name))
						"""

	def get_conn(self):
		# connect to db
		return mysql.connector.connect(user=self.username, password=self.password, host=self.rds_url, database=self.database_name)


	def save_video(self, name, s3_url):
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
		return


	def get_videos(self, specific_id=None):
		# defend against SQL injection attack
		if not specific_id == None and not isinstance(specific_id, int):
			raise exception.Exception('specific_id parameter must be an integer')
		conn = self.get_conn()
		cursor = conn.cursor()
		sql = "SELECT id, name, timestamp, rating, num_ratings, s3_url, streaming_url FROM videos"
		if (specific_id):
			sql = sql + " WHERE id = " + str(specific_id)
		cursor.execute(sql)
		rows = cursor.fetchall()
		videos = []
		for (video_id, name, timestamp, rating, num_ratings, s3_url, streaming_url) in rows:
			videos.append({
				"id": video_id,
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
		return


	def rate_video(self, video_id, rating):
		videos = self.get_videos(video_id)
		if (len(videos) == 0):
			raise exception.Exception('Unable to rate video. Video not found.')
		video = videos[0]
		new_rating = self.get_new_rating(video['num_ratings'], video['rating'], rating)
		conn = self.get_conn()
		cursor = conn.cursor()
		params = {
			"rating": new_rating,
			"num_ratings": video['num_ratings'] + 1,
			"id": video_id
		}
		cursor.execute("UPDATE videos SET rating=%(rating)s, num_ratings=%(num_ratings)s WHERE id=%(id)s", params)
		conn.commit()
		conn.close()
		return new_rating


	def delete_video(self, video_id):
		conn = self.get_conn()
		cursor = conn.cursor()
		params = {
			"id": video_id
		}
		cursor.execute("DELETE FROM videos WHERE id=%(id)s", params)
		conn.commit()
		conn.close()
		return


	def recreate_table(self):
		conn = self.get_conn();
		cursor = conn.cursor()

		# deletes table if exists
		cursor.execute("DROP TABLE IF EXISTS {table_name}".format(table_name=self.table_name))

		# creates table
		cursor.execute(self.movies_table_sql)

		conn.commit() # commit() necessary, or changes are not saved
		conn.close()
		return


	# Gets the new average rating, baased on the number of previous ratings and the cumulative previous rating
	def get_new_rating(self, num_ratings, rating, new_rating):
		total_rating = num_ratings * rating
		return (total_rating + new_rating) / (num_ratings + 1)
