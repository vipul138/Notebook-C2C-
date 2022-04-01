from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://mftqnkwcqcadav:7ddfabc8f5b7391ccdf155149744227f64f5a01d2ef46b7191a94c6ecfd1e2c8@ec2-44-199-143-43.compute-1.amazonaws.com:5432/dejjdb6lf5efjc'
app.config['SECRET_KEY'] = 'secret'
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'     #its loaction of mail server eg- gmail, yahoo, etc
app.config['MAIL_PORT'] = 587     # port from email is sent to server
app.config['MAIL_USE_TLS'] = True   # security encryption purpose 
app.config['MAIL_USERNAME'] = 'vipulvishwakarma786@gmail.com'
app.config['MAIL_PASSWORD'] = 'vipulserver786'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

from project import routes


