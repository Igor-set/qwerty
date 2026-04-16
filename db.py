import sqlite3
from werkzeug.security import generate_password_hash

class Database:
	def __init__(self, db_path="db.db"):
		self.conn = sqlite3.connect(db_path, check_same_thread=False)
		self.cur = self.conn.cursor()


class ProductDB(Database):
	def __init__(self, db_path="db.db"):
		super().__init__()

	def get_all_products(self):
		r = self.cur.execute("SELECT * FROM products").fetchall()

		result = []
		for i in r:
			result.append(list(i))

		return result

	def get_product(self, iid):
		result = self.cur.execute("SELECT * FROM products WHERE id = ?", (iid,)).fetchall()
		return result

	def insert(self, name, description, price, photo, color):
		self.cur.execute(
			"INSERT INTO products VALUES (NULL, ?, ?, ?, ?, ?)",
			(name, description, price, photo, color)
		)
		self.conn.commit()

	def delete_product(self, id):
		self.cur.execute("DELETE FROM products WHERE id=?", (id,))


class UserDB(Database):
	def __init__(self, db_path="db.db"):
		super().__init__()

	def get_user_by_login(self, login):
		result = self.cur.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchall()
		if result:
			return result[0]
		return []

	def new_user(self, login, password, role="user"):
		password = generate_password_hash(password)
		
		self.cur.execute(
			"INSERT INTO users VALUES (NULL, ?, ?, ?, ?)",
			(login, password, role, "")
		)
		self.conn.commit()

	def get_basket(self, login):
		result = self.cur.execute("SELECT basket FROM users WHERE login = ?", (login,)).fetchall()
		return result[0][0]

	def get_basket_on_list(self, login):
		result = self.get_basket(login)
		if result=="":
			return []
		basket = list(map(lambda x: list(map(int, x.split("x"))), result.split(",")))
		return basket

	def __update_basket(self, username, basket):
		result = ""
		for i in basket:
			result += str(i[0]) + "x" + str(i[1]) + ","
		else:
			result = result[:-1]

		self.cur.execute(
			"""UPDATE users SET basket = ? WHERE login = ?""", 
			(result, username)
		)
		self.conn.commit()

	def add_product_in_basket(self, username, product_id, count=1):
		# 1x2,3x5
		basket = self.get_basket_on_list(username)
		for i in basket:
			if i[0] == product_id:
				i[1] += count
				break
		else:
			basket.append([product_id, count])
		
		
		self.__update_basket(username, basket)

	def del_product_in_basket(self, username, product_id, count=1):
		basket = self.get_basket(username).split(",")
		basket = list(map(lambda x: list(map(int, x.split("x"))), basket))
		
		for i in basket:
			if i[0] == product_id:
				i[1] -= count
				if i[1] <= 0:
					basket.remove(i)

		self.__update_basket(username, basket)
	def edit_login(self, new_user_name, old_user_name):

		self.cur.execute(
			"""UPDATE users SET login = ? WHERE login = ?""", 
			(new_user_name, old_user_name)
		)
		self.conn.commit()

	def edit_password(self,password,username):
		password = generate_password_hash(password)
		self.cur.execute(
			"""UPDATE users SET password = ? WHERE login = ?""", 
			(password, username)
		)
		self.conn.commit()
		

# db = UserDB()
# #print(db.get_basket_on_list("ufpfy"))
# bd = ProductDB()
# # print(db.get_product(1))

# print(db.get_basket_on_list("admin"))
# print(bd.get_all_products())