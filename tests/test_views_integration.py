import os
import unittest
from urlparse import urlparse

from werkzeug.security import generate_password_hash

#Configure our app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.models import Post, User
from blog.database import Base, engine, session

class TestViews(unittest.TestCase):
	def setUp(self):
		"""Test setup"""
		self.client = app.test_client()

		#Set up the tables in the database
		Base.metadata.create_all(engine)

		#Create an example user
		self.user_a = models.User(name="Alice", email ="alice@example.com",
			password=generate_password_hash("test"))
		self.user_b = models.User(name="Eddie", email="eddie@example.com",
			password=generate_password_hash("1234"))
		session.add_all([self.user_a, self.user_b])
		session.commit()

	def tearDown(self):
		""" Test teardown """
		#Remove the tables and all their data from the test database
		Base.metadata.drop_all(engine)

	def simulate_login(self):
		with self.client.session_transaction() as http_session:
			http_session["user_id"] = str(self.user_a.id)
			http_session["_fresh"] = True

	def add_test_post(self):
		self.simulate_login()
		response = self.client.post("/post/add", data={
			"title": "Test Post",
			"content": "Test content"
			})
		return response

	def testAddPost(self):
		self.simulate_login()
		response = self.add_test_post()

		self.assertEqual(response.status_code, 302)
		self.assertEqual(urlparse(response.location).path, "/")
		posts = session.query(models.Post).all()
		self.assertEqual(len(posts), 1)

		post = posts[0]
		self.assertEqual(post.title, "Test Post")
		self.assertEqual(post.content, "<p>Test content</p>\n")
		self.assertEqual(post.author, self.user_a)

	def testDeletePost(self):
		self.simulate_login()
		add_response = self.add_test_post()
		post = session.query(Post).first()
		delete_response = self.client.post("/post/{}/delete".format(post.id), data={"post_id": "{}".format(post.id)})
		count = len(session.query(Post).all())

		self.assertEqual(delete_response.status_code, 302)
		self.assertEqual(count, 0)
		self.assertEqual(session.query(Post).filter_by(id=post.id).first(), None)


if __name__ == "__main__":
	unittest.main()