from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_login import (LoginManager, login_user, logout_user, 
	login_required, current_user)

from db import *
from func import check_file
from user import *
from forms import LoginForm, RegistrationForm
from config import *

app = Flask(__name__, template_folder="templates")
app.debug = True 
app.config["SECRET_KEY"] = SECRET_KEY

db = ProductDB()
userdb = UserDB()

# для аутентификации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)

# декоратор для админа
def admin_required(f):
	@wraps(f)
	def decor(*args, **kwargs):
		if not current_user.is_authenticated:
			return redirect(url_for("login"))
		if not current_user.is_admin():
			return redirect(url_for("index"))
		return f(*args, **kwargs)
	return decor
# ====================

@app.route("/")
@app.route("/index")
def index():
	items = db.get_all_products()

	try:
		basket = userdb.get_basket_on_list(current_user.username)
	except:
		basket = []

	for i in range(len(items)):
		for j in basket:
			if j[0] == items[i][0]:
				items[i].append(j[1])
				break
		else:
			items[i].append(0)
	
	return render_template("pages/index.html", items=items)

@app.route("/about")
def about():
	return "Страница о нас"

@app.route("/lk")
def lk():
	return render_template("pages/lk.html")

@app.route("/basket")
def basket():
	if not current_user.is_authenticated:
		return redirect(url_for("regist"))

	basket = userdb.get_basket_on_list(current_user.username)
	items = []
	for i in basket:
		item = db.get_product(i[0])[0]
		items.append({
			"id": item[0],
			"name": item[1],
			"description": item[2],
			"price": item[3],
			"photo": item[4],
			"color": item[5],
			"count": i[1],
			"total": i[1] * item[3]
		})


	return render_template("pages/basket.html", basket=items)

from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify  # ← добавьте session, jsonify

@app.route('/add_basket', methods=['POST'])
def add_basket():
	# Поддержка и JSON и form данных
	if request.is_json:
		data = request.get_json()
	else:
		data = request.form
	
	item_id = data.get('item_id')
	userdb.add_product_in_basket(current_user.username, item_id)
	
	return jsonify({'status': 'success', 'item_id': item_id})

@app.route('/add', methods=['POST'])
def add():
	if request.form.get("action")=="plus":
		userdb.add_product_in_basket(current_user.username, int(request.form["id"]) )
	
	elif request.form.get("action")=="minus":
		userdb.del_product_in_basket(current_user.username, int(request.form["id"]) )
	return redirect(request.referrer or url_for("basket"))
@app.route('/del_basket', methods=['POST'])
def del_basket():
	# Поддержка и JSON и form данных
	if request.is_json:
		data = request.get_json()
	else:
		data = request.form
	
	item_id = data.get('item_id')
	userdb.del_product_in_basket(current_user.username, item_id)
	
	return jsonify({'status': 'success', 'item_id': item_id})

@app.route('/pay', methods=['GET'])
def pay():
	if not current_user.is_authenticated:
		return redirect(url_for("regist"))

	basket = userdb.get_basket_on_list(current_user.username)
	items = 0
	for i in basket:
		item = db.get_product(i[0])[0]
		items+=i[1]*item[3]
	return render_template("pages/pay.html",i=items)

@app.route("/product/<int:item_id>")
def product(item_id):
	item = list(db.get_product(item_id)[0])
	try:
		basket = userdb.get_basket_on_list(current_user.username)
	except:
		basket = []
	for i in range(len(basket)):
		if basket[i][0]==item[0]:
			item.append(basket[i][1])
			break
	else:
		item.append(0)

	return render_template("pages/product.html", item=item)

@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("index"))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.authenticate(form.username.data, form.password.data)

		if user:
			login_user(user)
			flash(["Успешный вход!", "green"])
			return redirect(url_for("index"))
		flash(["Неверный логин или пароль", "red"])
	return render_template("pages/login.html", form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash("Вы вышли из системы")
	return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def regist():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		username = form.username.data

		if userdb.get_user_by_login(username):
			flash("Логин уже занят")
			return render_template("pages/register.html", form=form)

		userdb.new_user(username, form.password.data)
		user = User(username)
		login_user(user)
		flash("Регистрация прошла успешно!")
		return redirect(url_for('index'))

	return render_template("pages/register.html", form=form)

@app.route("/admin/add-project", methods=["GET", "POST"])
@admin_required
def admin_add_project():
	if request.method == "POST":
		for key in request.form:
			if request.form[key] == "":
				flash(["Не все поля были заполнены!", "red"])
				return render_template("admin/add_project.html")

		file = request.files["photo"] # достаем отправленный файл

		# проверка что файл не пустой
		if file.filename == "":
			flash(["Не выбран файл", "red"])
			return render_template("admin/add_project.html")
		
		# проверка, что файл с верным расширением
		if file and check_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(f"static/photo/{filename}")

		db.insert(
			request.form["name"],
			request.form["description"],
			request.form["price"],
			filename,
			request.form["color"]
		)

		flash(["Товар добавлен!", "green"])
		return render_template("admin/add_project.html")
	return render_template("admin/add_project.html")

@app.route("/admin/del-product", methods=["GET", "POST"])
@admin_required
def admin_delete_product():
	products = db.get_all_products()

	if request.method == "POST":
		del_id = request.form["id"]
		db.delete_product(int(del_id))
		
		return render_template("admin/del_project.html", products=products)

	return render_template("admin/del_project.html", products=products)


@app.route("/edit_lk", methods=["POST","GET"])
def edit_lk():
	if "login" in request.form:
		print (current_user)
		
		userdb.edit_login(request.form["login"], current_user.username)
		current_user.username=request.form["login"]
		current_user.id=request.form["login"]
	if "password" in request.form:
		userdb.edit_password(request.form["password"],current_user.username)
	return render_template("pages/edit_lk.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000)
