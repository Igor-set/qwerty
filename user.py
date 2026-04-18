from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from db import *

users_db = UserDB()

class User(UserMixin):
	def __init__(self, id):
		self.id = id
		self.username = id
		self.role = users_db.get_user_by_login(self.username)[3]

	@staticmethod
	def get(user_id):
		if users_db.get_user_by_login(user_id):
			return User(user_id)
		else:
			return None

	@staticmethod
	def authenticate(username, password):
		user_data = users_db.get_user_by_login(username)
		if user_data and check_password_hash(user_data[2], password):
			return User(username)
		else:
			return None

	def is_admin(self):
		return self.role == "admin"
		
	def edit_username(self,username):
		self.id=username
		self.username=username

