from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
	username = StringField("Логин", validators=[DataRequired()])
	password = PasswordField("Пароль", validators=[DataRequired()])
	sumbit = SubmitField("Войти")

class RegistrationForm(FlaskForm):
	username = StringField("Логин", validators=[DataRequired()])
	password = PasswordField("Пароль", validators=[DataRequired()])
	sumbit = SubmitField("Зарегистрироваться")